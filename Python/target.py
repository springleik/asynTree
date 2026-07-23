#!/usr/bin/env python3
# ============================================================
# Abstract syntax tree interpreter for motion control demo
# M. Williamsen, Springleik Project
# File target.py, 22 July 2026

import sys, time, json
import tkinter, threading

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
        self.done = False       # while !done
        self.lock = threading.Lock()
        self.flag = threading.Event()

        # create top level, set window title and position
        self.wind = tkinter.Toplevel()
        self.wind.title(self.name)
        motor.index += 1
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

def setRunCurrent(cmd):
    if len(cmd) == 2:   # return existing value
        axis = int(cmd[1], 0)
        if len(motor.axes) > axis:
            if hasattr(motor.axes[axis], 'runCurrent'):
                print('Axis: {}, runCurrent: {} milliamps.'.format (axis, motor.axes[axis].runCurrent))
            else:
                print('Attribute not found.')
        else:
            print ('Axis not found.')
    elif len(cmd) == 3: # set new value
        axis = int(cmd[1], 0)
        if len(motor.axes) > axis:
            motor.axes[axis].runCurrent = int(cmd[2],0)
            print('Axis: {}, runCurrent: {} milliamps.'.format (axis, motor.axes[axis].runCurrent))
        else:
            print('Axis not found.')
    else:               # usage text if wrong number of args
        print('Expected two arguments: axis number and run current (mA).')


# ============================================================
# thread to run console
def consX():
    done = False
    while not done:
        # tread carefully, due to notifier error on MacOS
        print ('@:', end = ' ')
        sys.stdout.flush()
        cmd = sys.stdin.readline().rstrip()

        # split commands and arguments
        cmd = cmd.split ()

        # ignore empty lines
        if len(cmd) == 0: continue

        # ignore comment lines
        if cmd[0][0] == '#': continue

        # interpret commands
        if cmd[0] == 'q':
            # motor objects are outside of tree structure
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
            done = True
            root.quit ()

        elif cmd[0] == 'initControl':
            # instantiate motors and command tree
            if 0 == len(motor.axes):
                motor.axes.append(motor('Motor 1', 210,  28))
                motor.axes.append(motor('Motor 2',  58, 354))
                motor.axes.append(motor('Motor 3', 362, 354))
            else:
                print('Control already initialized.')

        elif cmd[0] == 'setRunCurrent':
            setRunCurrent(cmd)
        # elif cmd[0] == 'setVelocity':
        #     if len (cmd) == 2: velocity = int (cmd[1], 0)
        #     print ('velocity: {} steps/second'.format (velocity))
        # elif cmd[0] == 'setAccel':
        #     if len (cmd) == 2: acceleration = int (cmd[1], 0)
        #     print ('acceleration: {} steps/second'.format (acceleration))
        # elif cmd[0] == 'homeAxis':
        #     pass
        # elif cmd[0] == 'setPosition':
        #     if len (cmd) == 2: position = int (cmd[1], 0)
        #     print ('position: {} steps/second'.format (position))
        # elif cmd[0] == 'waitPosition':
        #     pass
        # elif cmd[0] == 'iterateRegister':
        #     pass
        # elif cmd[0] == 'testInput':
        #     pass
        # elif cmd[0] == 'summarize':
        #     if theTree:
        #         print ('Tree contains {} nodes.'.format(theTree.summarize(0, 1)))
        #     else:
        #         print ('Empty tree.')

        elif cmd[0] == 'help' or cmd[0] == '?':
            print ('Available commands:')
            print (' q -- quit')
            print (' r -- run command tree')
            print (' help -- print this list')
            print (' initControl -- initialize motion controller')
            print (' summarize -- update node and depth counters')
            print (' setCurrent -- set motor current')
            print (' setVelocity -- set motor velocity in steps/second')
            print (' setAccel -- set motor acceleration in steps/sec/sec')
            print (' setPosition -- set target position in steps')
            print (' homeAxis -- home specified axis')
            print (' waitPosition -- wait for target position reached')
            print (' iterateRegister -- loop while iterating register')
            print (' testInput -- test a digital input')

        else:
            print ('Say what?')

# kick off console thread to interact with user
console = threading.Thread(target = consX)
console.start()

# invoke Tkinter main loop, which blocks until all windows are closed
# this must be in Python's main thread
root = tkinter.Tk()
root.mainloop()

# join console thread on exit
console.join()
