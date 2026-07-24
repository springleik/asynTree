#!/usr/bin/env python3
# ============================================================
# pseudoCode.py, Motion control program for motor simulation
# Renders a JSON representation of the control program as pseudocode.
# M. Williamsen, Springleik Project
# File pseudoCode.py
# 16 May 2026

import json, sys

inFileName = "ctrlX.json"

# check for command line args
args = sys.argv
if len (args) > 1: inFileName = args [1]

# load control program
print ('Loading control program file: {}'.format(inFileName))
ctrlTree = None
with open (inFileName) as inFile:
    ctrlTree = json.load (inFile)

# render via recursive descent
def render (cursor, level):
    theKind = cursor['kind']
    theName = cursor['name']
    if theKind == 'loop':
        print ('{}{}: Iterate {} times.'.format(
            '  ' * level, theName, cursor ['count']))
    elif theKind == 'delay':
        print ('{}{}: Wait for {} seconds.'.format(
            '  ' * level, theName, cursor['wait']))
    elif theKind == 'move':
        print ('{}{} to target {} with increment {} deg.'.format(
            '  ' * level, theName, cursor['targ'], cursor ['incr']))
    elif theKind == 'doneWait':
        print ('{}{} target reached.'.format('  ' * level, theName))
    elif theKind == 'keyWait':
        print ('{}{} input.'.format('  ' * level, theName))
    else:
        print ('{}{}:'.format('  ' * level, theName))

    level += 1
    if 'list' in cursor:
        for node in cursor['list']:
            render (node, level)

if ctrlTree:
    cursor = ctrlTree
    level = 0
    render (cursor, level)
