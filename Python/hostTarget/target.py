#!/usr/bin/env python3
# ============================================================
# Abstract syntax tree interpreter for motion control demo
# M. Williamsen, Springleik Project
# File target.py, 22 July 2026

import sys, time, json
import tkinter, threading
import socket, socketserver

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
            self.data = self.data.strip()
            if self.data == b'close':
                notDone = False
                print ('Connection closed.')
                break

            # handle client input
            parseCommand(self.data.decode('utf-8'))
            # response = '{} typed: {}'.format(self.client_address, self.data.decode('utf-8'))
            # print(response)
            # self.wfile.write(bytes(response + '\r\n', 'ascii'))

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
    done = False    # set done flag to exit program

    def __init__(self, name, xPos, yPos):
        # initialize instance variables
        self.name = name        # axis window title
        self.xPos = xPos        # axis window position
        self.yPos = yPos
        self.rot = 0            # rotation
        self.targ = self.rot    # target
        self.incr = 1           # velocity
        self.run = False        # status
        self.done = False       # while !done
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

    # serialize motor instance attributes to JSON
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
        print('Expected two arguments: axis number and {}.'.format(theAttrib))
        return False
    if len(cmd) > 1:
        axis = int(cmd[1], 0)
        if axis < 0 or len(motor.axes) <= axis:
            print('Axis not found.')
            return False
        if len(cmd) > 2:
            setattr(motor.axes[axis], theAttrib, int(cmd[2],0))
        if hasattr(motor.axes[axis], theAttrib):
            print('Axis: {}, {}: {}'.format(axis, theAttrib,
                getattr(motor.axes[axis], theAttrib)))
        else:
            print('Attribute not found.')
            return False
    return True

# update axis target position, return True on error
def setPosition(cmd):
    if len(cmd) < 3:
        return
    axis = int(cmd[1], 0)
    if axis < 0 or len(motor.axes) <= axis:
        print('Axis not found.')
        return
    newTarget = int(cmd[2], 0)
    if hasattr(motor.axes[axis], 'velocity'):
        newVelocity = motor.axes[axis].velocity
        motor.axes[axis].movePosition(newTarget, newVelocity)
    else:
        print('Velocity not set.')
    return

# wait until target position reached, return True on error
def waitPosition(cmd):
    if len(cmd) == 1:
        print('Expected an argument: axis number.')
        return
    axis = int(cmd[1], 0)
    if axis < 0 or len(motor.axes) <= axis:
        print('Axis not found.')
        return
    motor.axes[axis].flag.wait()
    return

# drive an axis to home position
def homeAxis(cmd):
    if len(cmd) == 1:
        print('Expected an argument: axis number.')
        return
    axis = int(cmd[1], 0)
    if axis < 0 or len(motor.axes) <= axis:
        print('Axis not found.')
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
        print('Control already initialized.')

# halt program and exit
def haltProgram():
    with open('motorX.json', 'w') as motorFile:
        first = True
        motorFile.write('[')
        for axis in motor.axes:
            if first: first = False
            else: motorFile.write(',')
            axis.done = True
            axis.serialize(motorFile)
            print(axis.getSpeed(), axis.getPosition(), end = ' ')
        motorFile.write(']\n')
    print()
    motor.done = True
    root.quit()
    return

# show help text on console
def showHelp():
    print('Available commands:')
    print(' quit -- halt program and exit')
    print(' help -- print this list')
    print(' initControl -- initialize motion controller')
    print(' setRunCurrent -- set axis run current')
    print(' setIdleCurrent -- set axis idle current')
    print(' setVelocity -- set axis velocity in steps/second')
    print(' setAccel -- set axis acceleration in steps/sec/sec')
    print(' setPosition -- set axis target position in steps')
    print(' homeAxis -- home specified axis')
    print(' waitPosition -- wait for target position reached')
    print(' iterateRegister -- loop while iterating register')
    print(' testInput -- test a digital input')

def parseCommand(cmd):
    cmd = cmd.split ()      # split commands and arguments
    if len(cmd) == 0:
        return False        # ignore empty lines
    if cmd[0][0] == '#':
        return False        # ignore comment lines

    # interpret commands
    time.sleep(0.001)
    if cmd[0] == 'quit':
        haltProgram()
        return True
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
    # elif cmd[0] == 'testInput':
    elif cmd[0] == 'help' or cmd[0] == '?':
        showHelp()
    else:
        print('Say what?')
    return False

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
                if motor.done: break

    # wait for user input at command prompt
    while not motor.done:
        # tread carefully, due to notifier error on MacOS
        print('@:', end = ' ')
        sys.stdout.flush()
        cmd = sys.stdin.readline().rstrip()
        parseCommand(cmd)

# kick off console thread to interact with local user
consoleThread = threading.Thread(target = consX)
consoleThread.start()

# kick off socket thread to interact with remote user
tcpServer = TCPServer(('', 12345), TCPHandler)
tcpServer.daemon_threads = True
tcpThread = threading.Thread(target = tcpServer.serve_forever)
tcpThread.daemon = True
tcpThread.start()

# invoke Tkinter main loop, which blocks until all windows are closed
root = tkinter.Tk()
root.mainloop()

# join threads on exit
tcpServer.shutdown()
consoleThread.join()
