# hostTarget

Simulated target device exposes a TCP socket interface with a simple command interpreter. A separate host program acts as a client, interacting with the target and running an abstract syntax tree (AST) interpreter. Host and target can run on the same machine using the default IP address 'localhost' and default port number '12345'. Or they can be on different machines using IP addresses and a port that you've enabled for TCP communication. All of this is meant as a proof-of-concept, to give you some ideas about what's possible and what the level of effort might be for projects you have in mind.

We start in a terminal window by navigating to the right directory. Output shown is from MacOS, syntax may need adjustments for Linux and Windows. Run the Python script _target.py_ without arguments to launch a target server at port '12345'. You can run multiple servers as long as each has its own port number, but one is enough for now.

```
MarksiMac:hostTarget williamm$ pwd
/Users/williamm/Documents/Projects/asynTree/Python/hostTarget
MarksiMac:hostTarget williamm$ python3 target.py
 Usage: python3 target.py [port=12345 [file.scp]]
 listening at: ('', 12345)
@: ?
Available remote commands:
 quit -- halt program and exit
 help -- print this list
 initControl -- initialize motion controller
 setRunCurrent -- set axis run current in mA
 setHoldCurrent -- set axis hold current in mA
 setVelocity -- set axis velocity in steps/second
 setAccel -- set axis acceleration in steps/sec/sec
 setPosition -- set axis target position in degrees
 homeAxis -- home specified axis
 setFlags -- set state of emulated inputs and outputs
 waitPosition -- wait for target position reached
@: initControl
@: setVelocity 0 3
Axis: 0, velocity: 3
@: setPosition 0 90
Axis: 0, position: 90
@: homeAxis 0
@: quit
-1 (0, 0) 1 (0, 0) 1 (0, 0)
```

Here I've started the target server and typed some commands at the console prompt. If everything is working correctly you should see some Tkinter GUI windows, as in the following screen capture. Commands are case-sensitive. Note that motor axes start with zero velocity, which you have to change to make them move. Once this makes sense to you, you can run the target server again and open a socket connection to it using _telnet_, _Putty_, or any similar program.

```
MarksiMac:hostTarget williamm$ telnet localhost 12345
Trying 127.0.0.1...
Connected to localhost.
Escape character is '^]'.
@: ?
Available remote commands:
 quit -- halt program and exit
 help -- print this list
 initControl -- initialize motion controller
 setRunCurrent -- set axis run current in mA
 setHoldCurrent -- set axis hold current in mA
 setVelocity -- set axis velocity in steps/second
 setAccel -- set axis acceleration in steps/sec/sec
 setPosition -- set axis target position in degrees
 homeAxis -- home specified axis
 setFlags -- set state of emulated inputs and outputs
 waitPosition -- wait for target position reached
@: initControl
@: setVelocity 1 -3
Axis: 1, velocity: -3
@: setPosition 1 -90
Axis: 1, position: -90
@: homeAxis 1
@: quit
Connection closed by foreign host.
MarksiMac:hostTarget williamm$
```
Here I've used command line _telnet_ to open the connection. For most commands the results and output are the same as they were at the console prompt. One exception is the 'quit' command, which when typed in _telnet_ closes the socket connection but leaves the server running. Also some commands will show a line of output on the server console, to help with troubleshooting. This proof-of-concept has no provisions for limiting or securing access to the target server. As written it even supports multiple clients connected at the same time, although they are not aware of each other. Real applications would have to address these issues.
