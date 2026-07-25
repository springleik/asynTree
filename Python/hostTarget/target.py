#!/usr/bin/env python3
# ============================================================
# Abstract syntax tree interpreter for motion control demo
# M. Williamsen, Springleik Project
# File target.py, 22 July 2026
# exposes TCP server allowing multiple connections

import sys, time, json
import tkinter, threading
import socket, socketserver

class globals:
    # global class variables
    done = False    # set done flag to exit program
    reply = ''
    inputs = 0
    lock = threading.Lock()

class TCPHandler(socketserver.StreamRequestHandler):
    def handle(self):
        # maintain connection until dropped or closed
        notDone = True
        while notDone:
            # show prompt
            theThread = threading.current_thread()
            thePrompt = '@: '
            self.wfile.write(bytes(thePrompt, 'ascii'))

            # check for dropped connection
            self.data = self.rfile.readline()
            if not len(self.data):
                notDone = False
                print ('Connection dropped.')
                break

            # check for closed connection
            cmd = self.data.decode('utf-8').strip()
            if 'close' in cmd or 'quit' in cmd:
                notDone = False
                print ('Connection closed.')
                break

            # handle client input
            parseCommand(cmd)
            self.wfile.write(bytes(globals.reply, 'ascii'))

class TCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

# class representing a function motor
class motor:
    # class variables
    width = 300     # pixel size of axis window
    height = 300
    radius = 100    # pixel size of axis rotor
    arc = 270       # degrees arc of rotor
    index = 1       # sequence number
    axes = []       # axis list

    def __init__(self, name, xPos, yPos):
        # initialize instance variables
        self.name = name        # axis window title
        self.xPos = xPos        # axis window position
        self.yPos = yPos
        self.rot = 0            # rotation
        self.targ = self.rot    # target
        self.incr = 1           # velocity
        self.run = False        # status
        self.done = False       # while not done
        self.lock = threading.Lock()
        self.flag = threading.Event()

        # create top level, set window title and position
        self.wind = tkinter.Toplevel()
        self.wind.title(self.name)
        motor.index += 1
        time.sleep(0.1)
        self.wind.geometry ('{}x{}+{}+{}'.format (
            motor.width, motor.height, self.xPos, self.yPos))
        self.wind.resizable(width = False, height = False)

        # create the canvas
        self.canvas = tkinter.Canvas(self.wind, width = self.width, height = self.height)
        self.canvas.configure(bd = 0, highlightthickness = 0)
        self.canvas.pack()

        # set up events, start animation timer
        self.wind.bind('<Button-1>', lambda event: self.mousePressed(event))
        self.wind.bind('<Key>', lambda event: self.keyPressed(event))
        self.wind.bind('<Left>', lambda event: self.leftPressed(event))
        self.wind.bind('<Right>', lambda event: self.rightPressed(event))
        self.wind.bind('<Up>', lambda event: self.upPressed(event))
        self.wind.bind('<Down>', lambda event: self.downPressed(event))
        self.timerFired(25)
        self.redrawAll()

    # getters and setters for outside access
    def getRunning(self): return self.run
    def setRunning(self, b): self.run = b
    def getSpeed(self): return self.incr
    def setSpeed(self, s): self.incr = s
    def getPosition(self): return self.rot, self.targ
    def setPosition(self, r):
        self.rot = r
        self.targ = r

    # move to new target position, return False if already there
    # this is a critical section
    def movePosition(self, t, u):
        self.lock.acquire()
        r = self.rot
        if r != t:
            self.targ = t
            if r < t: self.incr = abs(u)
            else: self.incr = -abs(u)
            self.run = True
            self.flag.clear()
        else:
            self.run = False
            self.flag.set()
        self.lock.release()
        return self.run

    # draw motor shaft position
    def redrawAll(self):
        self.canvas.delete(tkinter.ALL)
        self.canvas.create_rectangle(0, 0, self.width, self.height,
            fill = 'lightgrey', width = 0)
        self.canvas.create_line(2, 150, 300, 150)
        self.canvas.create_line(150, 2, 150, 350)
        self.canvas.create_arc(150 - motor.radius, 150 - motor.radius, 150 + motor.radius,
            150 + motor.radius, start = self.rot, extent = motor.arc, fill = 'white')
        text = 'rotation: {}\n target: {}'.format(self.rot, self.targ)
        self.canvas.create_text(10, 10, text = text, anchor = 'nw')
        self.canvas.update()

    # ignore mouse clicks for now
    # should only fire if this is the active window
    def mousePressed(self, event): pass

    # handle key pressed
    def keyPressed(self, event):
        c = event.char
        if 'q' == c:
            print('Closing ' + self.name)
            self.run = False
            self.done = True
            self.wind.destroy()
            self.wind = None
        elif 'r' == c: self.run = True
        elif 's' == c: self.run = False

    # handle arrow keys
    def leftPressed(self, event):
        self.rot -= 45
        self.run = True
    def rightPressed(self, event):
        self.rot += 45
        self.run = True
    def upPressed(self, event): self.incr += 1
    def downPressed(self, event): self.incr -= 1

    # pause, then call timerFired again unless done
    def timerFired(self, interval):
        # handle case where window doesn't exist
        if self.wind:
            if not self.wind.winfo_exists():
                pass
        # handle case where user closes program
        if self.done:
            self.run = False
            if self.wind:
                self.wind.destroy()
                self.wind = None
            pass
        # handle normal iteration
        # this is a critical section
        if self.run:
            self.lock.acquire()
            self.rot += self.incr
            if abs(self.rot - self.targ) <= abs(self.incr):
                self.rot = self.targ
                self.run = False
                self.flag.set()
            self.lock.release()
            self.redrawAll()
        # wait for next interval
        self.canvas.after(interval, self.timerFired, interval)

    # serialize motor class and instance attributes to JSON
    def serialize(self, jFile):
        jsonValues = {}
        for key, value in vars(self).items():
            if '.' not in str(type(value)):
                jsonValues[key] = value
        json.dump(jsonValues, jFile, indent = 2)

# ============================================================
# command functions
# set axis attributes, return True on error
def setAttribute(cmd, theAttrib):
    if len(cmd) == 1:
        globals.reply = 'Expected two arguments: axis number and {}.\n'.format(theAttrib)
        return False
    if len(cmd) > 1:
        axis = int(cmd[1], 0)
        if axis < 0 or len(motor.axes) <= axis:
            globals.reply = ('Axis not found.\n')
            return False
        if len(cmd) > 2:
            setattr(motor.axes[axis], theAttrib, int(cmd[2],0))
        if hasattr(motor.axes[axis], theAttrib):
            globals.reply = ('Axis: {}, {}: {}\n'.format(axis, theAttrib,
                getattr(motor.axes[axis], theAttrib)))
        else:
            globals.reply = ('Attribute not found.\n')
            return False
    return True

# update axis target position, return True on error
def setPosition(cmd):
    if len(cmd) < 3:
        return
    axis = int(cmd[1], 0)
    if axis < 0 or len(motor.axes) <= axis:
        globals.reply = 'Axis not found.\n'
        return
    newTarget = int(cmd[2], 0)
    if hasattr(motor.axes[axis], 'velocity'):
        newVelocity = motor.axes[axis].velocity
        motor.axes[axis].movePosition(newTarget, newVelocity)
    else:
        globals.reply = 'Velocity not set.\n'
    return

# update emulated digital inputs
def setInputs(cmd):
    if len(cmd) > 1:
        globals.inputs = int(cmd[1], 0)
    globals.reply = 'Digital inputs: {}\n'.format(hex(globals.inputs))

# wait until target position reached, return True on error
def waitPosition(cmd):
    if len(cmd) == 1:
        globals.reply = 'Expected an argument: axis number.\n'
        return
    axis = int(cmd[1], 0)
    if axis < 0 or len(motor.axes) <= axis:
        globals.reply = 'Axis not found.\n'
        return
    motor.axes[axis].flag.wait()
    return

# drive an axis to home position
def homeAxis(cmd):
    if len(cmd) == 1:
        globals.reply = 'Expected an argument: axis number.\n'
        return
    axis = int(cmd[1], 0)
    if axis < 0 or len(motor.axes) <= axis:
        globals.reply = 'Axis not found.\n'
        return
    motor.axes[axis].movePosition(0, 1)
    return

# initialize multi-axis motion controller
def initializeControl():
    if 0 == len(motor.axes):
        motor.axes.append(motor('Motor 1', 210,  28))
        motor.axes.append(motor('Motor 2',  58, 354))
        motor.axes.append(motor('Motor 3', 362, 354))
    else:
        globals.reply = 'Control already initialized.\n'

# halt program and exit
def haltProgram():
    first = True
    with open('motorX.json', 'w') as motorFile:
        motorFile.write('[')
        # class variables first, integers only
        classValues = {}
        for key, value in vars(motor).items():
            if type(value) == type(int(0)):
                classValues[key] = value
        json.dump(classValues, motorFile, indent = 2)

        # then instance variables for each axis
        for axis in motor.axes:
            if first: first = False
            motorFile.write(',')
            axis.done = True
            axis.serialize(motorFile)
            print(axis.getSpeed(), axis.getPosition(), end = ' ')
        motorFile.write(']\n')
        if not first: print()
    globals.done = True
    root.quit()
    return

# show help text on console
def showHelp():
    globals.reply = ('Available commands:\n' +
    ' quit -- halt program and exit\n' +
    ' help -- print this list\n' +
    ' initControl -- initialize motion controller\n' +
    ' setRunCurrent -- set axis run current\n' +
    ' setIdleCurrent -- set axis idle current\n' +
    ' setVelocity -- set axis velocity in steps/second\n' +
    ' setAccel -- set axis acceleration in steps/sec/sec\n' +
    ' setPosition -- set axis target position in steps\n' +
    ' homeAxis -- home specified axis\n' +
    ' setInputs -- set state of emulated inputs\n' +
    ' waitPosition -- wait for target position reached\n')

def parseCommand(cmd):
    globals.lock.acquire()  # this is a critical section
    globals.reply = ''      # clear reply string
    cmd = cmd.split ()      # split commands and arguments
    time.sleep(0.001)

    # interpret commands
    if len(cmd) == 0:
        pass            # ignore empty lines
    elif cmd[0][0] == '#':
        pass            # ignore comment lines
    elif cmd[0] == 'quit':
        haltProgram()
    elif cmd[0] == 'initControl':
        initializeControl()
    elif cmd[0] == 'setRunCurrent':
        setAttribute(cmd, 'runCurrent')
    elif cmd[0] == 'setIdleCurrent':
        setAttribute(cmd, 'idleCurrent')
    elif cmd[0] == 'setVelocity':
        setAttribute(cmd, 'velocity')
    elif cmd[0] == 'setAccel':
        setAttribute(cmd, 'acceleration')
    elif cmd[0] == 'setPosition':
        if setAttribute(cmd, 'position'):
            setPosition(cmd)
    elif cmd[0] == 'waitPosition':
        waitPosition(cmd)
    elif cmd[0] == 'homeAxis':
        homeAxis(cmd)
    elif cmd[0] == 'setInputs':
        setInputs(cmd)
    elif cmd[0] == 'help' or cmd[0] == '?':
        showHelp()
    else:
        print('Say what?')
    globals.lock.release()
    return

# ============================================================
# thread to run console
def consX():
    # check for file name argument
    if len(sys.argv) == 2:
        inFileName = sys.argv[1]
        with open(inFileName) as inFile:
            print('Reading file: {}.'.format(inFileName))
            for line in inFile:
                parseCommand(line)
                print(globals.reply, end = '')
                if globals.done: break

    # wait for user input at command prompt
    while not globals.done:
        # tread carefully, due to notifier error on MacOS
        print('@:', end = ' ')
        sys.stdout.flush()
        cmd = sys.stdin.readline().strip()
        parseCommand(cmd)
        print(globals.reply, end = '')

# kick off socket thread to interact with remote user
socketserver.TCPServer.allow_reuse_address = True
tcpServer = TCPServer(('', 12345), TCPHandler)
tcpServer.daemon_threads = True
tcpThread = threading.Thread(target = tcpServer.serve_forever)
tcpThread.daemon = True
tcpThread.start()

# kick off console thread to interact with local user
consoleThread = threading.Thread(target = consX)
consoleThread.start()

# invoke Tkinter main loop, which blocks until all windows are closed
root = tkinter.Tk()
root.mainloop()

# join threads on exit
tcpServer.shutdown()
consoleThread.join()
