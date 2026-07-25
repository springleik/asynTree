#!/usr/bin/env python3
# ============================================================
# Abstract syntax tree interpreter for motion control demo
# M. Williamsen, Springleik Project
# File host.py, 22 July 2026
# implements TCP client to connect to target

import socket, sys

# default settings, modify to suit application
HOST, PORT = "localhost", 12345
fileName = ''

# check command line args
args = sys.argv
if len(args) == 1:
    print(' Usage: host.py [host=localhost [port=12345 [file]]]')
if len(args) > 1:
    HOST = args[1]
if len(args) > 2:
    PORT = int(args[2], 0)
if len(args) > 3:
    fileName = args[3]

# Create a TCP socket and connect to host
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect((HOST, PORT))

    # check for script file
    if fileName:
        print('file: ', fileName)

    # prompt for user input
    done = False
    while not done:
        reply = str(sock.recv(1024), 'utf-8')
        if not len(reply):
            done = True
            print('Connection dropped.')
        else:
            print(reply, end = '')
            sys.stdout.flush()
            cmd = sys.stdin.readline()
            sock.sendall(bytes(cmd, 'utf-8'))
