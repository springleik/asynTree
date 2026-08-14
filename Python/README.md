# Abstract Syntax Tree (AST) interpreters in Python

This folder currently contains three sub-project folders:

* __asynTree__ Skeleton interpreter runs on the command line, produces a JSON file and come console text.
* __hostTarget__ Simulated target device exposes a TCP socket interface with a simple command interpreter. Separate host program acts as a client, interacting with the target and running an AST interpreter.
* __toyMotor__ Self-contained GUI demo uses Tkinter to simulate a three-axis motion control system controlled by an AST interpreter.

Each of these folders has its own _ReadMe_ file explaining what's there and how to use it.
