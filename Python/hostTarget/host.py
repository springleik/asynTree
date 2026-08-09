#!/usr/bin/env python3
# ============================================================
# Abstract syntax tree interpreter for motion control demo
# M. Williamsen, Springleik Project
# File host.py, 22 July 2026
# implements TCP client to connect to target server

import socket, sys, json

# default settings, modify to suit application
HOST, PORT = "localhost", 12345
fileName = ''

# check command line args
args = sys.argv
if len(args) == 1:
    print(' Usage: python3 host.py [host=localhost [port=12345 [file.scp]]]')
if len(args) > 1:
    HOST = args[1]
if len(args) > 2:
    PORT = int(args[2], 0)
if len(args) > 3:
    fileName = args[3]

# abstract base class for tree nodes
class node():
    tree = {}       # global class variable
    done = False    # global exit flag

# leaf nodes represent commands being sent to target
class leaf(node):
    def __init__(self):
        self.cmd = '# empty'

    # send command to remote
    def executeCmd(self, cmd = ''):
        if not cmd: cmd = self.cmd
        sock.sendall(bytes(cmd + '\n', 'utf-8'))
        # receive reply, check connection
        reply = str(sock.recv(1024), 'utf-8')
        if not len(reply):
            print('Connection dropped.')
            node.done = True
        else:
            # save reply minus the prompt
            reply = reply[:-3].strip()
            if reply:
                self.reply = reply
                print(reply)

    # override this method to subclass
    def execute(self, cmd = ''):
        self.executeCmd(cmd)

    # render attributes as JSON text
    def serializeAttr(self, file, indent):
        jsonValues = {}
        for key, value in vars(self).items():
            if (key != 'list') and ('.' not in str(type(value))):
                jsonValues[key] = value
        print(json.dumps(jsonValues).strip('{}'), end = '', file = file)

    # override this method to subclass
    def serialize(self, file, indent):
        print(indent * '  ' + '{', end = '', file = file)
        self.serializeAttr(file, indent)
        print('}', end = '', file = file)

# branch nodes represent iteration and flow control
class branch(leaf):
    # traverse and execute subordinate nodes
    def executeList(self):
        if hasattr(self, 'list'):
            for item in self.list:
                item.execute()

    # override this method to subclass
    def execute(self):
        self.executeCmd()
        self.executeList()

    # traverse and serialize subordinate nodes
    def serializeList(self, file, indent):
        if hasattr(self, 'list'):
            print (', "list": [', file = file)
            first = True
            for item in self.list:
                if first: first = False
                else: print(',', file = file)
                item.serialize(file, indent + 1)
            print(']', end = '', file = file)

    # override this method to subclass
    def serialize(self, file, indent = 0):
        print(indent * '  ' + '{', end = '', file = file)
        self.serializeAttr(file, indent)
        self.serializeList(file, indent)
        print('}', end = '', file = file)

    # compose node tree
    def append(self, item):
        if not hasattr(self, 'list'):
            self.list = []
        self.list.append(item)

# initControl command
class initControl(branch):
    def __init__(self):
        self.cmd = 'initControl'

# setRunCurrent command
class setRunCurrent(leaf):
    def __init__(self, axis = None, current_mA = None):
        self.cmd = 'setRunCurrent'
        if axis != None: self.axis = axis
        if current_mA != None: self.current_mA = current_mA

    def execute(self):
        cmd = self.cmd
        if hasattr(self, 'axis'): cmd += ' {}'.format(self.axis)
        if hasattr(self, 'current_mA'): cmd += ' {}'.format(self.current_mA)
        super().execute(cmd)

# setIdleCurrent command
class setIdleCurrent(leaf):
    def __init__(self, axis = None, current_mA = None):
        self.cmd = 'setIdleCurrent'
        if axis != None: self.axis = axis
        if current_mA != None: self.current_mA = current_mA

    def execute(self):
        cmd = self.cmd
        if hasattr(self, 'axis'): cmd += ' {}'.format(self.axis)
        if hasattr(self, 'current_mA'): cmd += ' {}'.format(self.current_mA)
        super().execute(cmd)

# setVelocity command
class setVelocity(leaf):
    def __init__(self, axis = None, steps_sec = None):
        self.cmd = 'setVelocity'
        if axis != None: self.axis = axis
        if steps_sec != None: self.steps_sec = steps_sec

    def execute(self):
        cmd = self.cmd
        if hasattr(self, 'axis'): cmd += ' {}'.format(self.axis)
        if hasattr(self, 'steps_sec'): cmd += ' {}'.format(self.steps_sec)
        super().execute(cmd)

# setAccel command
class setAccel(leaf):
    def __init__(self, axis = None, steps_sec2 = None):
        self.cmd = 'setAccel'
        if axis != None: self.axis = axis
        if steps_sec2 != None: self.steps_sec2 = steps_sec2

    def execute(self):
        cmd = self.cmd
        if hasattr(self, 'axis'): cmd += ' {}'.format(self.axis)
        if hasattr(self, 'steps_sec2'): cmd += ' {}'.format(self.steps_sec2)
        super().execute(cmd)

# homeAxis command
class homeAxis(leaf):
    def __init__(self, axis = None):
        self.cmd = 'homeAxis'
        if axis != None: self.axis = axis

    def execute(self):
        cmd = self.cmd
        if hasattr(self, 'axis'): cmd += ' {}'.format(self.axis)
        super().execute(cmd)

# setPosition command
class setPosition(leaf):
    def __init__(self, axis = None, steps = None):
        self.cmd = 'setPosition'
        if axis != None: self.axis = axis
        if steps != None: self.steps = steps

    def execute(self):
        cmd = self.cmd
        if hasattr(self, 'axis'): cmd += ' {}'.format(self.axis)
        if hasattr(self, 'steps'): cmd += ' {}'.format(self.steps)
        super().execute(cmd)

# waitPosition command
class waitPosition(leaf):
    def __init__(self, axis = None):
        self.cmd = 'waitPosition'
        if axis != None: self.axis = axis

    def execute(self):
        cmd = self.cmd
        if hasattr(self, 'axis'): cmd += ' {}'.format(self.axis)
        super().execute(cmd)

# check state of digital inputs
class testInput(branch):
    def __init__(self, digIn, trueIf):
        self.cmd = 'testInput'
        self.digIn = digIn
        self.trueIf = trueIf

    # traverse and execute subordinate nodes if condition true
    def execute(self):
        # obtain input state
        self.executeCmd('setInputs')
        # test input state
        descend = False
        if hasattr(self, 'reply'):
            reply = self.reply.split()
            if len(reply) == 3:
                inputs = int(reply[2], 0)
                if hasattr(self, 'digIn'):
                    inBit = inputs & (1 << self.digIn)
                    if hasattr(self, 'trueIf'):
                        descend = (bool(inBit) == bool(self.trueIf))
        if descend:
        # descend to next level if states match
            self.executeList()

# loop over a register value
class iterateRegister(branch):
    def __init__(self, reg, start, stop, step = 1):
        self.cmd = 'iterateRegister'
        self.reg = reg
        self.start = start
        self.stop = stop
        self.step = step

    def execute(self):
        if hasattr(self, 'list'):
            for n in range(self.start, self.stop, self.step):
                self.executeList()

# factory method to instantiate local command trees
# figure numbers match those in the arXiv paper
def figureFactory(cmd):
    if len(cmd) == 1:
        print('Expected numeric argument.')
        return
    index = int(cmd[1], 0)

    # flat instruction list from figure 1
    if index == 1:
        node.tree = branch()
        node.tree.append(initControl())
        node.tree.append(setRunCurrent(1, 500))
        node.tree.append(setIdleCurrent(1, 500))
        node.tree.append(setVelocity(1, 10))
        node.tree.append(setAccel(1, 10))
        node.tree.append(homeAxis(1))
        node.tree.append(waitPosition(1))
        node.tree.append(setPosition(1, 200))
        node.tree.append(waitPosition(1))
        node.tree.append(setPosition(1, 0))
        node.tree.append(waitPosition(1))
        node.tree.append(setPosition(1))

    # composite command tree from figure 2
    elif index == 2:
        node.tree = initControl()
        node.tree.append(setRunCurrent(1, 500))
        node.tree.append(homeAxis(1))
        node.tree.append(setVelocity(1, 10))
        node.tree.append(setAccel(1, 10))
        node.tree.append(setRunCurrent(2, 500))
        node.tree.append(homeAxis(2))
        node.tree.append(setVelocity(2, 10))
        node.tree.append(setAccel(2, 10))
        outerLoop = iterateRegister(0, 200, 20)
        node.tree.append(outerLoop)
        outerLoop.append(setPosition(1, -1))
        outerLoop.append(waitPosition(1))
        innerLoop = iterateRegister(0, 100, 10)
        outerLoop.append(innerLoop)
        innerLoop.append(setPosition(2, -2))
        innerLoop.append(waitPosition(2))
        testBranch = testInput(1, 1)
        node.tree.append(testBranch)
        testBranch.append(setIdleCurrent(1, 50))
        testBranch.append(setIdleCurrent(2,25))

    else:
        print('Unexpected index.')

# help text for local command handler
def localHelp():
    print('Available local commands:\n' +
    ' figure N      -- compose command tree for figure N\n' +
    ' execute       -- execute command tree\n' +
    ' serial [file] -- render command tree as JSON text\n' +
    ' clear         -- delete command tree\n' +
    ' close         -- close remote connection and exit\n' +
    ' ?             -- print this list')

# local command handler
# return true if local command
# return false if remote command
def localCommand(cmd):
    cmd = cmd.split()
    if 0 == len(cmd):
        pass
    elif cmd[0] == '#':
        pass
    elif 'figu' in cmd[0]:
        figureFactory(cmd)
    elif 'exec' in cmd[0]:
        if node.tree:
            node.tree.execute()
        else:
            print('Nothing to execute.')
    elif 'seri' in cmd[0]:
        if node.tree:
            if len(cmd) == 1:
                node.tree.serialize(sys.stdout)
                print()
            else:
                with open(cmd[1], 'w') as file:
                    node.tree.serialize(file)
                    print(file = file)
        else:
            print('Nothing to serialize.')
    elif 'clea' in cmd[0]:
        if node.tree:
            node.tree = None
        else:
            print('Nothing to clear.')
    elif cmd[0] == '?':
        localHelp()
    else:
        return False
    print('@:', end = ' ', flush = True)
    return True

# Create a TCP socket to connect to target
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect((HOST, PORT))

    # consume first prompt
    prompt = sock.recv(1024)
    print(str(prompt, 'utf-8'), end = '', flush = True)

    # check for script file
    # remote commands only
    if fileName:
        with open(fileName) as inFile:
            for line in inFile:
                # skip empty lines and comments
                if len(line.strip()) == 0 or line[0] == '#':
                    continue
                if not localCommand(line):
                    # send command to target
                    sock.sendall(bytes(line, 'utf-8'))
                    # receive reply, check connection
                    reply = str(sock.recv(1024), 'utf-8')
                    if not len(reply):
                        print('Connection dropped.')
                        node.done = True
                        break
                    else:
                        print(reply, end = '', flush = True)

    # console prompt for user input
    while not node.done:
        cmd = sys.stdin.readline()
        # send to local command handler
        if not localCommand(cmd):
            # if not a local command, it must be remote
            sock.sendall(bytes(cmd, 'utf-8'))
            # receive reply, check connection
            reply = str(sock.recv(1024), 'utf-8')
            if not len(reply):
                print('Connection dropped.')
                node.done = True
            else:
                print(reply, end = '', flush = True)
