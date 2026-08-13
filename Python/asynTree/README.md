# asynTree
Abstract Syntax Tree (AST) interpreters in Python.

This is a skeleton interpreter framework, which could be developed into a small domain-specific language. Run it at the command line without arguments and get some console text showing what happened, and a JSON file rendering the interpreter's command tree. Here is what that looks like in a MacOS terminal window. Windows and Linux require some adjustments to the syntax.

```
MarksiMac:asynTree williamm$ pwd
/Users/williamm/Documents/Projects/asynTree/Python/asynTree

MarksiMac:asynTree williamm$ python3 asynTree.py > asynTree.txt

MarksiMac:asynTree williamm$ ../CompTree.py asynTreeRef.json asynTree.json
[]

MarksiMac:asynTree williamm$ git diff asynTree.txt
MarksiMac:asynTree williamm$
```

First make sure you have navigated to the right directory. Then run the Python script asynTree.py. In this example I've redirected the console output to the file asynTree.txt. Running the script will create or overwrite the file asynTree.json. We can compare it to a checked-in reference file using CompTree.py one level up. Finally we use git to see if anything changed in the console output. Now it's your turn, to make changes in the source code and see how the output changes.
