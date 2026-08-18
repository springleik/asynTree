/*
 * File asynTree.h declares an
 * Abstract Syntax Tree Interpreter
 * M. Williamsen, Springleik Project
 * 20 June 2024
*/

// https://stackoverflow.com/questions/21150454/representing-an-abstract-syntax-tree-in-c

// common interface for all nodes
typedef struct node
{
    // instance variables
    int depth;
    int seq;
    struct node *next;  // singly linked list at the same level
    struct node *list;  // singly linked list at level beneath

    // instance method pointers allow polymorphic behavior
    void (*execute) (void *this);
    void (*serial)  (void *this);
} node;

// node is first, so <what> can be cast to <node>
typedef struct what
{
    node base;
    int one;
    int two;
    int three;
} what;

typedef enum {false, true} boolean;

// base class instance methods
void release (void *this);
void append  (void *this, void *that);
void summary (void *this, int depth, int *pseq);

// override instance methods for subclasses
void executeNode (void *this);
void serialNode  (void *this);

void executeWhat (void *this);
void serialWhat  (void *this);
