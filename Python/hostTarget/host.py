#!/usr/bin/env python3
# ============================================================
# Abstract syntax tree interpreter for motion control demo
# M. Williamsen, Springleik Project
# File host.py, 22 July 2026
# implements TCP client to connect to target server

import socket, sys

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
    tree = []
    def __init__(self, name):
        self.name = name

    def execute(self):
        pass

    def serialize(self):
        pass

# leaf nodes represent commands being sent to target
class leaf(node):
    def __init__(self, name):
        super().__init__(name)

    def execute(self):
        pass

    def serialize(self):
        pass

# branch nodes represent iteration and flow control
class branch(node):
    def __init__(self, name):
        super().__init__(name)
        self.list = []

    def execute(self):
        for item in self.list:
            item.execute()

    def serialize(self):
        for item in self.list:
            item.serialize()

    def append(self, item):
        node.list.append(item)

# factory method to instantiate local command trees
# figure numbers match those in the arXiv paper
def figureFactory(cmd):
    node.tree = [leaf('a'), leaf('b'), leaf('c')]
    print(node.tree)

# local command handler
# return false if command not recognized
def localCommand(cmd):
    cmd = cmd.split()
    if 0 == len(cmd):
        return False
    elif 'fig' in cmd[0]:
        figureFactory(cmd)
    elif 'exec' in cmd[0]:
        for item in node.tree:
            item.execute()
    elif 'serial' in cmd[0]:
        for item in node.tree:
            item.serialize()
    elif cmd[0] == 'help':
        print('Some help...')
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
    done = False
    if fileName:
        with open(fileName) as inFile:
            for line in inFile:
                # skip empty lines and comments
                if len(line.strip()) == 0 or line[0] == '#':
                    continue
                # send command to target
                sock.sendall(bytes(line, 'utf-8'))
                # receive reply, check connection
                reply = str(sock.recv(1024), 'utf-8')
                if not len(reply):
                    print('Connection dropped.')
                    done = True
                print(reply, end = '', flush = True)

    # console prompt for user input
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
