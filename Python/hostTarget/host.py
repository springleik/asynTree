#!/usr/bin/env python3
# ============================================================
# Abstract syntax tree interpreter for motion control demo
# M. Williamsen, Springleik Project
# File host.py, 22 July 2026
# implements TCP client to connect to target

import socket, sys

HOST, PORT = "localhost", 12345
data = " ".join(sys.argv[1:])

print("Sent:     {}".format(data))

# Create a socket (SOCK_STREAM means a TCP socket)
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    # Connect to server and send data
    sock.connect((HOST, PORT))
    sock.sendall(bytes(data + "\n", "utf-8"))

    # receive data from the server and shut down
    # discard first prompt
    print('Recd: ',str(sock.recv(1024), "utf-8").strip())
    print('Recd: ',str(sock.recv(1024), "utf-8").strip())
    sock.shutdown(socket.SHUT_RDWR)
