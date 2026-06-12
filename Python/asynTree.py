#!/usr/bin/env python3
# ------------------------ AST.py ------------------------ #
# M. Williamsen, FlexLink, 5 April 2024

# Consider possible demonstrations
# Strip chart recorder showing position, velocity, acceleration vs. time
# Strip chart recorder showing quantity per unit time of products passing a sensor
# Strip chart of products entering or leaving a combiner, diverter, etc
# showing peak throughput for each channel. Yay!
# Animation, as in my crankshaft program, with the possibility to slow it down arbitrarily to show dependencies
# Emergency stop and reset
# State machine evolution
# Forcing inputs via buttons on screen
# And then finally doing everything as above, but connected to a real motor on a real conveyor line
# Motor jog and run commands would be nice, in all modes
# Interesting to compare class instances vs. dictionaries for tree nodes
# Dictionaries and lists are mutable, and so are class objects

import time, math

# Root class for polymorphic tree nodes
class node:
    # Each leaf node has an optional value
    # which can be any JSON-compatible type
    def __init__(self, aValue = None):
        self.value = aValue
        self.level = 0
        self.count = 0
        pass
        
    def execute(self):
        print ('Executing node')
        pass
        
    def analyze(self):
        print ('Analyzing node')
        pass
        
    def serializeValue(self):
        theValue = self.value
        theType = type(theValue)
        if theValue is True: print ('true', end = '')
        elif theValue is False: print ('false', end = '')
        elif theValue is None: print ('null', end = '')
        elif theType is int: print (theValue, end = '')
        elif theType is str: print ('"' + theValue + '"', end = '')
        elif theType is float:
            if math.isnan(theValue): print ('NaN', end = '')
            elif math.isinf(theValue): print ('Infinity', end = '')
            else: print (theValue, end = '')        

    def serialize(self):
        print ('{{"level":{0},"count":{1},"value":'.format(self.level, self.count), end = '')
        self.serializeValue()
        print ('}', end = '')
        
    def summarize(self, visitor = None):
        if visitor is None: visitor = node('visitor')
        self.level = visitor.level
        self.count = visitor.count
        visitor.count += 1
       
# Subclass with a list
class branch (node):
    # Each branch node has an optional value and series
    def __init__(self, aValue = None, aSeries = None):
        super().__init__(aValue)
        if aSeries: self.series = aSeries
        else: self.series = []

    def enter (self):
        print ('Entering branch')
        pass
        
    def leave (self):
        print ('Leaving branch')
        pass
        
    def execute(self):
        print ('Executing branch')
        self.enter()
        for item in self.series:
            item.execute()
        self.leave()
        
    def analyze(self):
        print ('Analyzing branch')
        for item in self.series:
            item.analyze()
        pass
        
    def serialize(self):
        print ('{"value":', end = '')
        self.serializeValue()
        print (',"level":{0},"count":{1},"series":['.format(self.level, self.count), end = '')
        first = True
        for item in self.series:
            if first: first = False
            else: print (',', end = '')
            print ('\n' + item.level * '   ', end = '')
            item.serialize()
        print ('\n' + self.level * '   ' + ']}', end = '')
        
    def summarize(self, visitor = None):
        if visitor is None: visitor = node('visitor')
        super().summarize(visitor)
        visitor.count += 1
        visitor.level += 1
        for item in self.series:
            item.summarize(visitor)
        visitor.level -= 1
        
    def append(self, item):
        self.series.append(item)
        pass

# leaf subclass for time delay
class wait (node):
    def execute(self):
        print ('Waiting: {0} seconds.'.format(self.value))
        time.sleep (self.value)
        pass

# branch subclass for loop iteration
class loop (branch):        
    def execute(self):
        remain = self.value
        while self.value > 0:
            super().execute()
            self.value -= 1

# compose a tree of nodes
aTree = loop(3,
    [
        node(1),
        node('two'),
        node(False),
        wait(0.25),
        branch(55,
            [
                node(2),
                node('three'),
                node(True),
                node(None),
                wait(0.1),
                node(math.inf),
                node(math.nan)
            ]
        ),
        branch(12345,
            [
                node(123),
                node(1.23)
            ]
        )
    ]
)

# summarize the tree
aTree.summarize()

# execute the tree
aTree.execute()

# analyze the tree
aTree.analyze()

# serialize the tree
aTree.serialize()
