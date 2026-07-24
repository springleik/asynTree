# ============================================================
# motorSim.py, Simple animation model for function motors
# M. Williamsen, Springleik Project
# File motorSim.py
# 14 May 2024

import tkinter, threading, json
# ============================================================
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
