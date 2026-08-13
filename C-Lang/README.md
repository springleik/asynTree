# asynTree
Abstract Syntax Tree (AST) interpreters in C language.

Initial implementation is a skeleton interpreter framework, which could be developed into a small domain-specific language. Assuming we use TCP sockets for inter-process communication, this will be done for Linux/Unix targets first. Following is a simple build and test workflow in a MacOS terminal window. Syntax may need some adjustment for Linux and Windows.

```
MarksiMac:C-Lang williamm$ gcc asynTree.c -o asynTree

MarksiMac:C-Lang williamm$ ./asynTree 1> asynTree.json 2> asynTree.txt

MarksiMac:C-Lang williamm$ ../Python/CompTree.py asynTreeRef.json asynTree.json
[]

MarksiMac:C-Lang williamm$ git diff asynTree.txt
MarksiMac:C-Lang williamm$
```

First build the executable, done here with _gcc_. Then run the program, redirecting _stdout_ to a JSON file and _stderr_ to a TXT file. We verify the output by performing an asymmetric tree compare between a checked-in reference file and the new file _asynTree.json_. The empty square brackets indicate no differences were found. Finally we use _git_ to look for differences in the text output. Apparently none were found. All good! Now you can start making changes and looking for them in the output.
