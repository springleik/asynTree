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
    System.err.println("hello, world");
    
	// instantiate tree nodes
    node one = new node ();
    node two = new node ();
    node three = new node ();
    node four = new node ();
    node five = new node ();
    node six = new node ();
    node seven = new node ();
    node eight = new node ();
    node nine = new node ();
    node ten = new what (1, 2, 3);
    node eleven = new what (4, 5, 6);
	System.err.printf ("nodeCount: %d\n", node.nodeCount);
    
    // compose the tree
    one.append (two);
    one.append (three);
    one.append (four);
    one.append (five);
    one.append (six);
    three.append (seven);
    three.append (eight);
    three.append (nine);
    two.append (ten);
    ten.append (eleven);
    
    // execute and serialize the tree to console
    one.execute ();
    one.serial (0);
	System.out.println ();
	
	// check status
	System.err.printf ("nodeCount: %d\n", node.nodeCount);
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
	}
	
	// common code for serialization
	void serialCommon (int theDepth) {
		// entry code
		System.out.printf (",\"depth\":%d", theDepth++);
		System.out.printf (",\"seq\":%d", seq);
		System.out.printf (",\"list\":[");
		
		// iterate over child nodes
        boolean first = true;
        for (node aNode: theList) {
            if (first) {
                first = false;
            }
            else {
                // separator for two or more child nodes
                System.out.print (",");
            }
            System.out.println ();
            aNode.serial (theDepth);
        }
		
		// exit code
		System.out.print ("]}");
	}
	
    // serialize this node recursively
    void serial (int theDepth) {
        // entry code
        if (0 != theDepth) {
			// indent output if needed
			System.out.printf ("%" + (theDepth * 3) + "s", "");
		}
		System.out.printf ("{\"type\":\"node\"");

        // invoke common code
        serialCommon (theDepth);
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
	
	// constructor for what
	what (int a, int b, int c) {
		one   = a;
		two   = b;
		three = c;
	}
	
    // serialize what recursively
    void serial (int theDepth) {
        // entry code
        if (0 != theDepth) {
			// indent output if needed
			System.out.printf ("%" + (theDepth * 3) + "s", "");
		}
		System.out.printf ("{\"type\":\"what\"");
		System.out.printf (",\"one\":%d", one);
		System.out.printf (",\"two\":%d", two);
		System.out.printf (",\"three\":%d", three);

        // invoke common code
        serialCommon (theDepth);
    }
}
