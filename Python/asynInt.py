# ============================================================
# asynInt.py, Abstract syntax tree interpreter for motion control
# M. Williamsen, FlexLink AB
# 14 May 2024

import time, json
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

    # TODO goal to serialize to string, file, or console
    def serialize(self, jFile):
        s = json.dumps(self.data)[:-1] + ',"list":['
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
        self.data['key'] = key
        
    def execute(self):
        time.sleep(1.0)