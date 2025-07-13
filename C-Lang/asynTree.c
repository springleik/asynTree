/*
 * File asynTree.c defines an
 * Abstract Syntax Tree Interpreter
 * M. Williamsen, 20 June 2024
*/

// https://github.com/zserge/jsmn/tree/master
// https://stackoverflow.com/questions/21150454/representing-an-abstract-syntax-tree-in-c
// https://stackoverflow.com/questions/840501/how-do-function-pointers-in-c-work

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <assert.h>

#include "jsmn.h"
#include "asynTree.h"

// helper functions to simplify syntax for base class methods
void execute (void *p) {((node *)p)->execute(p);}
void serial  (void *p) {((node *)p)->serial(p);}

// ----------------------------------------------------------------
// base class instance methods

// do once for each node, before composing syntax tree
int nodeCount = 0;  // global count of mallocs and frees
void initNode (node *this)
{
    assert (this);
    this->list = NULL;
    this->next = NULL;
    this->depth = 0;
    this->seq = 0;
    this->execute = executeNode;
    this->serial = serialNode;
    nodeCount++;
}

// execute all nodes by recursive descent
void executeNode (void *this)
{
    // entry code
    assert (this);

    // iterate over child nodes
    node *p = ((node *)this)->list;
    while (p)
    {
        execute(p);
        p = p->next;
    }

    // exit code
}

// common code for serialization
void serialCommon (void *this)
{
    // entry code
    assert (this);
    node *p = (node *) this;
    printf (",\"depth\":%d", p->depth);
    printf (",\"seq\":%d", p->seq);
    printf (",\"list\":[");

    // iterate over child nodes
    boolean first = true;
    p = p->list;
    while (p)
    {
        if (first) {first = false;}
        else {printf (",");}
        printf ("\n");
        serial(p);
        p = p->next;
    }

    // exit code
    printf ("]}");
}

// serialize all nodes by recursive descent
void serialNode (void *this)
{
    // entry code
    assert (this);
    printf ("%*s", ((node *)this)->depth * 3, "");
    printf ("{\"type\":\"node\"");

    // invoke common code
    serialCommon (this);
}

// free all nodes by recursive descent
// only for nodes created on the heap
void release (void *this)
{
    // entry code
    assert (this);

    // iterate over child nodes
    node *p = ((node *)this)->list;
    while (p)
    {
        node *q = p;
        p = p->next;
        release(q);
    }

    // exit code
    free (this);
    nodeCount--;
}

// add a node to the tree, beneath this
void append (void *this, void *that)
{
    // entry code
    assert (this);
    assert (that);

    // check if list exists
    node *p = (node *) this;
    if (p->list)
    {
        // append to existing list
        node *q = p->list;
        while (q->next) {q = q->next;}
        q->next = that;
    }
    else
    {
        // start a new list
        p->list = that;
    }

    // exit code
}

// summarize tree by recursive descent
void summary (void *this, int depth, int *pseq)
{
    // entry code
    assert (this);
    node *p = (node *) this;
    p->depth = depth++;
    p->seq = (*pseq)++;

    // iterate over child nodes
    p = p->list;
    while (p)
    {
        summary(p, depth, pseq);
        p = p->next;
    }

    // exit code
}

// ----------------------------------------------------------------
// subclass instance methods

// do once for subclassed nodes
void initWhat (what *this)
{
    // invoke base class initialization
    node *p = (node *) this;
    initNode (p);

    // override instance methods
    p->serial = serialWhat;
    p->execute = executeWhat;

    // initialize subclass instance variables
    this->one = 1;
    this->two = 2;
    this->three = 3;
}

// execute subclass by recursive descent
void executeWhat (void *this)
{
    // entry code
    assert (this);
    what *p = (what *) this;
    printf ("Executing what one: %d, two: %d, three: %d\n", p->one, p->two, p->three);

    // invoke base class iteration
    executeNode (this);

    // exit code
}

// serialize subclass by recursive descent
void serialWhat (void *this)
{
    // entry code
    assert (this);
    what *p = (what *) this;
    printf ("%*s", p->base.depth * 3, "");
    printf ("{\"type\":\"what\"");
    printf (",\"one\":%d", p->one);
    printf (",\"two\":%d", p->two);
    printf (",\"three\":%d", p->three);

    // invoke common code
    serialCommon (this);
}

// ----------------------------------------------------------------
// main entry point
int main(void)
{
    // instantiate a node
    printf ("hello, world\n");
    node *first = malloc (sizeof(node));
    initNode (first);
    printf ("one: %d, two: %d\n", first->depth, first->seq);

    // instantiate a JSON parser
    char *jsn = "{\"one\":1,\"two\":2,\"three\":3,\"four\":4}";
    jsmn_parser par;
    jsmntok_t tok [16];
    jsmn_init (&par);
    int tokens = jsmn_parse (&par, jsn, strlen(jsn), tok, 16);
    printf ("tokens: %d\n", tokens);

    // allocate tree nodes
    node *one = malloc (sizeof(node));
    node *two = malloc (sizeof(node));
    node *three = malloc (sizeof(node));
    node *four = malloc (sizeof(node));
    node *five = malloc (sizeof(node));
    node *six = malloc (sizeof(node));
    node *seven = malloc (sizeof(node));
    node *eight = malloc (sizeof(node));
    node *nine = malloc (sizeof(node));
    what *ten = malloc (sizeof(what));
    what *eleven = malloc (sizeof(what));

    // initialize tree nodes
    printf ("nodeCount: %d\n", nodeCount);
    initNode (one);
    initNode (two);
    initNode (three);
    initNode (four);
    initNode (five);
    initNode (six);
    initNode (seven);
    initNode (eight);
    initNode (nine);
    initWhat (ten);
    initWhat (eleven);

    // adjust some variables
    eleven->one = 4;
    eleven->two = 5;
    eleven->three = 6;

    // compose the tree
    append (one, two);
    append (one, three);
    append (one, four);
    append (one, five);
    append (one, six);
    append (three, seven);
    append (three, eight);
    append (three, nine);
    append (two, ten);
    append (ten, eleven);

    // execute and serialize the tree to console
    int seq = 0;
    summary (one, 0, &seq);
    printf ("nodeCount: %d, seq: %d\n", nodeCount, seq);
    execute (one);
    serial (one);
    printf ("\n");
    release(one);
    printf ("nodeCount: %d\n", nodeCount);
    release(first);
    printf ("nodeCount: %d\n", nodeCount);
}
