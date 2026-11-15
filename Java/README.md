# Abstract Syntax Tree (AST) interpreter in Java

Initial implementation is a skeleton interpreter framework, which could be developed into a small domain-specific language. Eventual goal is to support both host and target functionality in Java command line programs, using TCP sockets for inter-process communication. Following is a simple build-and-test workflow in a MacOS terminal window. Syntax may need some adjustment for Linux and Windows.

```
MarksiMac:Java williamm$ pwd
/Users/williamm/Documents/Projects/asynTree/Java

MarksiMac:Java williamm$ javac asynTree.java

MarksiMac:Java williamm$ java asynTree 1> asynTree.json 2> asynTree.txt

MarksiMac:Java williamm$ python3 ../Python/CompTree.py asynTreeRef.json asynTree.json
[]

MarksiMac:Java williamm$ git diff asynTree.txt
MarksiMac:Java williamm$
```

Check that you are in the right folder and build the executable, done here with _javac_. Then run the program, redirecting _stdout_ to a JSON file and _stderr_ to a TXT file. We verify the output by performing an asymmetric tree comparison between a checked-in reference file and the new file _asynTree.json_. The empty square brackets indicate no differences were found. Finally we use _git_ to look for differences in the text output file _asynTree.txt_. Apparently none were found. All good! Now you can start making changes and looking for them in the output.
