# ============================================================
# asynInt.py, Abstract syntax tree interpreter for motion control
# M. Williamsen, Springleik Project
# File asynInt.py
# 14 May 2024

import sys, time, json
import tkinter, threading, json

# ============================================================
# global variables
current = 0         # milliamps
velocity = 0        # steps/second
acceleration = 0    # steps/second/second
position = 0        # steps

# ============================================================
# classes to implement abstract syntax tree (AST)
class node:
    # Each node has a value which is a data dictionary
    # and a series which is a list of subordinate nodes
    def __init__(self, theName = ''):
        self.data = {}                  # each node is a dictionary
        self.series = []                # each node has a list
        self.data['kind'] = 'node'      # placed here for serialization
        self.data['name'] = theName

    # add nodes to this nodes list
    def append(self, *nodes):
        for node in nodes:
            self.series.append(node)

    # override to add entry and exit code
    def execute(self):
        for item in self.series:
            item.execute()

    def analyze(self):
        for item in self.series:
            item.analyze()

    # serialize to file
    def serialize(self, jFile):
        s = json.dumps(self.data, indent = 2)[:-1] + ',"list":['
        print(s, file = jFile, end = '')
        first = True
        for item in self.series:
            if first: first = False
            else: print(',', file = jFile, end = '')
            item.serialize(jFile)
        print(']}', file = jFile, end = '')

    # add up levels and node numb
    def summarize(self, depth = None, numb = None):
        if depth is None: depth = 0
        if numb is None: numb = 1
        self.data['depth'] = depth
        self.data['numb'] = numb
        for item in self.series:
            numb = item.summarize(depth + 1, numb + 1)
        return numb

# motor initiate move command
class move(node):
    def __init__(self, name, motor, target, increment):
        super().__init__(name)
        self.data['kind'] = 'move'

        # motor object isn't serializable for now
        self.motor = motor
        self.data['motor'] = motor.name
        self.data['targ'] = target
        self.data['incr'] = increment

    def execute(self):
        self.motor.movePosition(self.data['targ'], self.data['incr'])
        for item in self.series:
            item.execute()

# motor wait for motion done command
class doneWait(node):
    def __init__(self, name, motor):
        super().__init__(name)
        self.data['kind'] = 'doneWait'
        self.motor = motor
        self.data['motor'] = motor.name

    def execute(self):
        self.motor.flag.wait()
        for item in self.series:
            item.execute()

# iteration command
class loop(node):
    def __init__(self, name, numb):
        super().__init__(name)
        self.data['kind'] = 'loop'
        self.data['numb'] = numb

    def execute(self):
        for n in range(self.data['numb']):
            for item in self.series:
                item.execute()

class delay(node):
    def __init__(self, name, interval):
        super().__init__(name)
        self.data['kind'] = 'delay'
        self.data['wait'] = interval

    def execute(self):
        time.sleep(self.data['wait'])
        for item in self.series:
            item.execute()

class keyWait(node):
    def __init__(self, name, key):
        super().__init__(name)
        self.data['kind'] = 'keyWait'
        self.data['key'] = key

    def execute(self):
        time.sleep(1.0)

# class representing a function motor
class motor:
    # class variables
    width = 300
    height = 300
    radius = 100
    arc = 270
    index = 1

    def __init__(self, name):
        # initialize instance variables
        self.name = name
        self.rot = 0
        self.targ = self.rot
        self.incr = 1
        self.run = False
        self.done = False
        self.lock = threading.Lock()
        self.flag = threading.Event()

        # create top level, set window title and position
        self.wind = tkinter.Toplevel()
        self.wind.title(self.name)
        if 1 == motor.index:
            motor.xPos, motor.yPos = 210, 28
        elif 2 == motor.index:
            motor.xPos, motor.yPos = 58, 354
        elif 3 == motor.index:
            motor.xPos, motor.yPos = 362, 354
        else: print ('Unexpected index: {}'.format (index))
        motor.index += 1
        self.wind.geometry ('{}x{}+{}+{}'.format (
            motor.width, motor.height, motor.xPos, motor.yPos))
        self.wind.resizable(width = False, height = False)

        # create the canvas
        self.canvas = tkinter.Canvas(self.wind, width = self.width, height = self.height)
        self.canvas.configure(bd = 0, highlightthickness = 0)
        self.canvas.pack()

        # set up events, start animation timer
        self.wind.bind("<Button-1>", lambda event: self.mousePressed(event))
        self.wind.bind("<Key>", lambda event: self.keyPressed(event))
        self.wind.bind("<Left>", lambda event: self.leftPressed(event))
        self.wind.bind("<Right>", lambda event: self.rightPressed(event))
        self.wind.bind("<Up>", lambda event: self.upPressed(event))
        self.wind.bind("<Down>", lambda event: self.downPressed(event))
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
        print (json.dumps(jsonValues, indent = 2), end = '', file = jFile)

'''
Pseudocode for motion profile:

Top Level
    Initialize all motors to receive products
    Iterate until halted
        Forward a product to track 1
            Move motor 1 and motor 2 fast to home position (135)
            Wait for motors 1 and 2
            Wait for product to arrive at motor 1 (key 'i')
            Move motor 1 slow to left position (270)
            Wait for product to arrive at motor 2 (key 'j')
            Move motor 2 slow to left position (270)
            Move motor 1 fast to home position
            Wait for motor 2
            Wait for product to arrive at track 1 (key 'o')
            Move motor 2 fast to home position (135)

        Forward a product to track 2
            Move motor 1 and motor 2 fast to home position (135)
            Wait for motors 1 and 2
            Wait for product to arrive at motor 1 (key 'i')
            Move motor 1 slow to left position (270)
            Wait for product to arrive at motor 2 (key 'j')
            Move motor 2 slow to right position (0)
            Move motor 1 fast to home position
            Wait for motor 2
            Wait for product to arrive at track 1 (key 'o')
            Move motor 2 fast to home position (135)

        Forward a product to track 3
            Move motor 1 and motor 3 fast to home position (135)
            Wait for motors 1 and 3
            Wait for product to arrive at motor 1 (key 'i')
            Move motor 1 slow to right position (0)
            Wait for product to arrive at motor 3 (key 'k')
            Move motor 3 slow to left position (270)
            Move motor 1 fast to home position
            Wait for motor 3
            Wait for product to arrive at track 1 (key 'o')
            Move motor 3 fast to home position (135)

        Forward a product to track 4
            Move motor 1 and motor 3 fast to home position (135)
            Wait for motors 1 and 3
            Wait for product to arrive at motor 1 (key 'i')
            Move motor 1 slow to right position (0)
            Wait for product to arrive at motor 3 (key 'k')
            Move motor 3 slow to right position (270)
            Move motor 1 fast to home position
            Wait for motor 3
            Wait for product to arrive at track 1 (key 'o')
            Move motor 3 fast to home position (135)
'''

# ============================================================
# factory method returns a command tree
# global constants follow
homePos = 135
leftPos = 270
rightPos = 0
fastSpeed = 15
slowSpeed = 3

# factory method to produce a subtree
def ctrlY(theTrack):
    if theTrack == 1:
        posA = leftPos
        posB = leftPos
        motB = motor2
        text = 'motor 2'
    elif theTrack == 2:
        posA = leftPos
        posB = rightPos
        motB = motor2
        text = 'motor 2'
    elif theTrack == 3:
        posA = rightPos
        posB = leftPos
        motB = motor3
        text = 'motor 3'
    elif theTrack == 4:
        posA = rightPos
        posB = rightPos
        motB = motor3
        text = 'motor 3'
    else:
        print ('Unexpected track: {}'.format(theTrack))
        return None

    subTree = node('Track #{}'.format(str(theTrack)))
    subTree.append(
        move('Move motor 1', motor1, homePos, fastSpeed),
        move('Move ' + text, motB, homePos, fastSpeed),
        doneWait('Wait for motor 1', motor1),
        keyWait('Wait for key i', 'i'),
        doneWait('Wait for ' + text, motB),
        move('Move motor 1', motor1, posA, slowSpeed),
        doneWait('Wait for motor 1', motor1),
        keyWait('Wait for key o', 'o'),
        move('Move motor 1', motor1, homePos, fastSpeed),
        move('Move ' + text, motB, posB, slowSpeed),
        doneWait('Wait for ' + text, motB),
        delay('Wait track 1', 1.0),
        move('Move ' + text, motB, homePos, fastSpeed))

    return subTree

# return a command tree implementing the desired program
def ctrlX(name):
    # instantiate some nodes
    top = loop(name, 3)
    top.append(ctrlY(1), ctrlY(2), ctrlY(3), ctrlY(4))
    return top

# ============================================================
# thread to run console
# this thread can invoke a command tree
def consX():
    global current, velocity, acceleration, position
    global root, motor1, motor2, motor3
    
    done = False
    while not done:
        # tread carefully, due to notifier error on MacOS
        print ('@:', end = ' ')
        sys.stdout.flush()
        cmd = sys.stdin.readline().rstrip()

        # interpret commands
        if 'q' == cmd:
            motor1.done = True
            motor2.done = True
            motor3.done = True
            done = True
            root.quit ()
        elif 'r' == cmd: theTree.execute()

        # split commands and arguments
        cmd = cmd.split ()
        if cmd[0] == "initControl":
            # instantiate motors and command tree
            motor1 = motor('Motor 1')
            motor2 = motor('Motor 2')
            motor3 = motor('Motor 3')
            theTree = ctrlX('Motor Control')
        elif cmd[0] == "setCurrent":
            if len (cmd) == 2: current = int (cmd[1], 0)
            print ("current: {} milliamps".format (current))
        elif cmd[0] == "setVelocity":
            if len (cmd) == 2: velocity = int (cmd[1], 0)
            print ("velocity: {} steps/second".format (velocity))
        elif cmd[0] == "setAccel":
            if len (cmd) == 2: acceleration = int (cmd[1], 0)
            print ("acceleration: {} steps/second".format (acceleration))
        elif cmd[0] == "homeAxis":
            pass
        elif cmd[0] == "setPosition":
            if len (cmd) == 2: position = int (cmd[1], 0)
            print ("position: {} steps/second".format (position))
        elif cmd[0] == "waitPosition":
            pass
        elif cmd[0] == "iterateRegister":
            pass
        elif cmd[0] == "testInput":
            pass

        else: print ('what?')


# kick off console thread to interact with user
console = threading.Thread(target = consX)
console.start()

# invoke Tkinter main loop, which blocks until all windows are closed
# this must be in Python's main thread
root = tkinter.Tk()
root.mainloop()

# join threads
console.join()

# capture tree state on exit
with open('ctrlX.json', 'w') as treeFile:
    theTree.serialize(treeFile)
    treeFile.write('\n')

# motor objects are outside of tree structure
with open('motorX.json', 'w') as motorFile:
    motorFile.write('[')
    motor1.serialize(motorFile)
    motorFile.write(',')
    motor2.serialize(motorFile)
    motorFile.write(',')
    motor3.serialize(motorFile)
    motorFile.write(']\n')

# show console output
print(motor1.getSpeed(), motor1.getPosition(), motor2.getSpeed(),
    motor2.getPosition(), motor3.getSpeed(), motor3.getPosition())
