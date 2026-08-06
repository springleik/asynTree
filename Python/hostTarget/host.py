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
    print(' Usage: host.py [host=localhost [port=12345 [file.scp]]]')
if len(args) > 1:
    HOST = args[1]
if len(args) > 2:
    PORT = int(args[2], 0)
if len(args) > 3:
    fileName = args[3]

# abstract base class for tree nodes
class node():
    tree = {}       # global class variable

# leaf nodes represent commands being sent to target
class leaf(node):
    def __init__(self):
        self.cmd = '# do nothing leaf'

    def execute(self, cmd = ''):
        if not cmd: cmd = self.cmd
        sock.sendall(bytes(cmd + '\n', 'utf-8'))
        # receive reply, check connection
        reply = str(sock.recv(1024), 'utf-8')
        if not len(reply):
            print('Connection dropped.')
            done = True
        else:
            reply = reply[:-3].strip()
            if reply:
                self.reply = reply
                print(reply)

    def serialize(self, first):
        if not first: print(',')
        jsonValues = {}
        for key, value in vars(self).items():
            if '.' not in str(type(value)):
                jsonValues[key] = value
        print(json.dumps(jsonValues), end = '')

# branch nodes represent iteration and flow control
class branch(node):
    def __init__(self):
        self.list = []

    def execute(self):
        for item in self.list:
            item.execute()

    def serialize(self, first):
        if not first: print(',', end = '')
        print ('{"list": [')
        first = True
        for item in self.list:
            item.serialize(first)
            if first: first = False
        print(']}')

    def append(self, item):
        self.list.append(item)

# initControl command
class initControl(leaf):
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

# factory method to instantiate local command trees
# figure numbers match those in the arXiv paper
def figureFactory(cmd):
    if len(cmd) == 1:
        print('Expected numeric argument.')
        return
    index = int(cmd[1], 0)

    # flat instruction list
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
    elif index == 2:
        pass
    else:
        print('Unexpected index.')

# help text for local command handler
def localHelp():
    print('Some help...')

# local command handler
# return true if local command
# return false if remote command
def localCommand(cmd):
    cmd = cmd.split()
    if 0 == len(cmd):
        pass
    elif cmd[0] == '#':
        pass
    elif 'fig' in cmd[0]:
        figureFactory(cmd)
    elif 'exec' in cmd[0]:
        if node.tree:
            node.tree.execute()
        else:
            print('Nothing to execute.')
    elif 'serial' in cmd[0]:
        if node.tree:
            node.tree.serialize(True)
        else:
            print('Nothing to serialize.')
    elif 'clear' in cmd[0]:
        if node.tree:
            node.tree = None
        else:
            print('Nothing to clear.')
    elif cmd[0] == 'help':
        localHelp()
    else:
        return False
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
                        done = True
                    else:
                        print(reply, end = '', flush = True)

    # console prompt for user input
    done = False
    while not done:
        cmd = sys.stdin.readline()
        # send to local command handler
        if not localCommand(cmd):
            # if not a local command, it must be remote
            sock.sendall(bytes(cmd, 'utf-8'))
            # receive reply, check connection
            reply = str(sock.recv(1024), 'utf-8')
            if not len(reply):
                print('Connection dropped.')
                done = True
            else:
                print(reply, end = '', flush = True)
