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

# Create a TCP socket to connect to target
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect((HOST, PORT))

    # consume first prompt
    prompt = sock.recv(1024)
    print(str(prompt, 'utf-8'), end = '')
    sys.stdout.flush()

    # check for script file
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
                print(reply, end = '')

    # console prompt for user input
    while not done:
        # send a command to target
        cmd = sys.stdin.readline()
        sock.sendall(bytes(cmd, 'utf-8'))

        # wait for reply from target
        reply = str(sock.recv(1024), 'utf-8')

        # check for lost connection
        if not len(reply):
            print('Connection dropped.')
            done = True
        else:
            print(reply, end = '')
            sys.stdout.flush()
