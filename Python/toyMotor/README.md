# toyMotor

Self-contained GUI demo uses Tkinter to simulate a three-axis motion control system controlled by an AST interpreter. Run it at the command line without arguments to get a console prompt and some GUI windows. Here is what that looks like in a MacOS terminal window. Windows and Linux require minor adjustments to the syntax.

```
MarksiMac:toyMotor williamm$ pwd
/Users/williamm/Documents/Projects/asynTree/Python/toyMotor

MarksiMac:toyMotor williamm$ python3 toyMotor.py
@: r
@: q
15 (135, 135) 15 (135, 135) 15 (135, 135)

MarksiMac:toyMotor williamm$ python3 ../CompTree.py motorXRef.json motorX.json
[]

MarksiMac:toyMotor williamm$ python3 ../CompTree.py ctrlXRef.json ctrlX.json
[]

MarksiMac:toyMotor williamm$ python3 pseudoCode.py > pseudoCode.txt
MarksiMac:toyMotor williamm$ git diff pseudoCode.txt
```

![GUI windows for Toy Motor Demo.](toyMotor.png)
