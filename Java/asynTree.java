/* Abstract Syntax Tree Framework
 * File asynTree.java
 * M. Williamsen, Springleik Project
 * 14 June 2026
 */

import java.util.List;
import java.util.ArrayList;

// Demonstrate abstract syntax tree technology

public class asynTree {
  public static void main(String[] args) {
    System.out.println("hello, world");
    
    node first = new node ();
    
    System.out.print (node.nodeCount);
    
    first.append (new node ());
    first.append (new node ());
    first.append (new what ());

    System.out.print (node.nodeCount);

	first.serial ();
  }
}

// composite class, may have child nodes
class node {
    // class members
	static int nodeCount;
	
    // instance members
    List <node> theList;
    int depth;
    int seq;

	// constructor
	node () {
		theList = new ArrayList <> ();
		depth = 0;
		seq = 0;
		nodeCount++;
		System.out.print ("-->new node");
	}
	
	// common code for serialization
	void serialCommon () {
		// entry code
		
		// iterate over child nodes
        boolean first = true;
        for (node aNode: theList) {
            if (first) {
                first = false;
            }
            else {
                // render interamble if two or more child nodes
                System.out.print ("b");
            }
            aNode.serial ();
        }
		
		// exit code
	}
	
    // serialize this node recursively
    void serial () {
        // entry code
        if (0 != depth) {
			// indent output if needed
			System.out.printf ("%" + (depth * 3) + "s", "");
		}
		System.out.printf ("{\"type\":\"node\"\n");

        // invoke common code
        serialCommon ();
    }
    
    // append that to this
    void append (node that) {
		theList.add (that);
	}
	
    // execute this node recursively
    void execute () {
		// entry code

		for (node aNode: theList) {
			// iterate over child nodes
			aNode.execute ();
		}

		// exit code

	}

    // summarize this branch node recursively
    void summary () {
		// entry code

		for (node aNode: theList) {
			// iterate over child nodes
			aNode.summary ();
		}
		// exit code
	}
}

class what extends node {
	// instance variables
	int one;
	int two;
	int three;
	
	// constructur for what node
	what () {
		one = 1;
		two = 2;
		three = 3;
	}
}
