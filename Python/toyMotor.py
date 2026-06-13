#!/usr/bin/env python3
# ============================================================
# Motion control program for motor simulation
# M. Williamsen, Springleik Project
# File toyMotor.py
# 14 May 2024

import tkinter, threading, json
import motorSim, asynInt, sys

'''
Pseudocode for motion profile:

Top Level
    Initialize all motors to receive products
    Iterate until halted
        Forward a product to track 1
            Move motor 1 and motor 2 fast to home position (135)
            Wait for motors 1 and 2
            Wait for product to arrive at motor 1 (key 'i')
            Move motor 1 slow to left position (270)
            Wait for product to arrive at motor 2 (key 'j')
            Move motor 2 slow to left position (270)
            Move motor 1 fast to home position
            Wait for motor 2
            Wait for product to arrive at track 1 (key 'o')
            Move motor 2 fast to home position (135)

        Forward a product to track 2
            Move motor 1 and motor 2 fast to home position (135)
            Wait for motors 1 and 2
            Wait for product to arrive at motor 1 (key 'i')
            Move motor 1 slow to left position (270)
            Wait for product to arrive at motor 2 (key 'j')
            Move motor 2 slow to right position (0)
            Move motor 1 fast to home position
            Wait for motor 2
            Wait for product to arrive at track 1 (key 'o')
            Move motor 2 fast to home position (135)

        Forward a product to track 3
            Move motor 1 and motor 3 fast to home position (135)
            Wait for motors 1 and 3
            Wait for product to arrive at motor 1 (key 'i')
            Move motor 1 slow to right position (0)
            Wait for product to arrive at motor 3 (key 'k')
            Move motor 3 slow to left position (270)
            Move motor 1 fast to home position
            Wait for motor 3
            Wait for product to arrive at track 1 (key 'o')
            Move motor 3 fast to home position (135)

        Forward a product to track 4
            Move motor 1 and motor 3 fast to home position (135)
            Wait for motors 1 and 3
            Wait for product to arrive at motor 1 (key 'i')
            Move motor 1 slow to right position (0)
            Wait for product to arrive at motor 3 (key 'k')
            Move motor 3 slow to right position (270)
            Move motor 1 fast to home position
            Wait for motor 3
            Wait for product to arrive at track 1 (key 'o')
            Move motor 3 fast to home position (135)
'''

# ============================================================
# factory method returns a command tree
# global constants follow
homePos = 135
leftPos = 270
rightPos = 0
fastSpeed = 15
slowSpeed = 3

# factory method to produce a subtree
def ctrlY(theTrack):
    if theTrack == 1:
        posA = leftPos
        posB = leftPos
        motB = motor2
        text = 'motor 2'
    elif theTrack == 2:
        posA = leftPos
        posB = rightPos
        motB = motor2
        text = 'motor 2'
    elif theTrack == 3:
        posA = rightPos
        posB = leftPos
        motB = motor3
        text = 'motor 3'
    elif theTrack == 4:
        posA = rightPos
        posB = rightPos
        motB = motor3
        text = 'motor 3'
    else:
        print ('Unexpected track: {}'.format(theTrack))
        return None

    subTree = asynInt.node('Track #{}'.format(str(theTrack)))
    subTree.append(
        asynInt.move('Move motor 1', motor1, homePos, fastSpeed),
        asynInt.move('Move ' + text, motB, homePos, fastSpeed),
        asynInt.doneWait('Wait for motor 1', motor1),
        asynInt.keyWait('Wait for key i', 'i'),
        asynInt.doneWait('Wait for ' + text, motB),
        asynInt.move('Move motor 1', motor1, posA, slowSpeed),
        asynInt.doneWait('Wait for motor 1', motor1),
        asynInt.keyWait('Wait for key o', 'o'),
        asynInt.move('Move motor 1', motor1, homePos, fastSpeed),
        asynInt.move('Move ' + text, motB, posB, slowSpeed),
        asynInt.doneWait('Wait for ' + text, motB),
        asynInt.delay('Wait track 1', 1.0),
        asynInt.move('Move ' + text, motB, homePos, fastSpeed))

    return subTree

# return a command tree implementing the desired program
def ctrlX(name):
    # instantiate some nodes
    top = asynInt.loop(name, 3)
    top.append(ctrlY(1), ctrlY(2), ctrlY(3), ctrlY(4))
    return top

# ============================================================
# thread to run console
# this thread can invoke a command tree
def consX():
    done = False
    while not done:
        # tread carefully, due to notifier error on MacOS
        print ('@:', end = ' ')
        sys.stdout.flush()
        cmd = sys.stdin.readline().rstrip()

        # interpret commands
        if 'q' == cmd: done = True
        elif 'r' == cmd: theTree.execute()
        else: print ('what?')

# ============================================================
# instantiate motors and command tree
root = tkinter.Tk()
motor1 = motorSim.motor('Motor 1')
motor2 = motorSim.motor('Motor 2')
motor3 = motorSim.motor('Motor 3')
theTree = ctrlX('Motor Control')

# kick off console thread to interact with user
console = threading.Thread(target = consX)
console.start()

# invoke Tkinter main loop, which blocks until all windows are closed
# this must be in Python's main thread
root.mainloop()

# join threads
console.join()

# capture state on exit
with open('ctrlX.json', 'w') as treeFile:
    theTree.serialize(treeFile)
    treeFile.write('\n')

with open('motorX.json', 'w') as motorFile:
    motorFile.write('[')
    motor1.serialize(motorFile)
    motorFile.write(',')
    motor2.serialize(motorFile)
    motorFile.write(',')
    motor3.serialize(motorFile)
    motorFile.write(']\n')

print(motor1.getSpeed(), motor1.getPosition(), motor2.getSpeed(),
    motor2.getPosition(), motor3.getSpeed(), motor3.getPosition())
