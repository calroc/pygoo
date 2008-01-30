#!/usr/bin/env python
'''
Demonstrate the iterable nature of the scan, parse, and format (to
ElementTree objects) stages of the widget creation pipeline.
'''
from pygoo import Scanner, Parser, Formatter


source = '''

    mickey = minnie
    larry=moe

    text
        width = 20
        height = 10
        sticky = nsew
        row = 1
        rowspan = 2
    .
    frame
        button
            text = plot
            <Button-1> = plotCallback
        .
        button
            sticky = nsew
            row = 1
            column = 1
        ..
    button
        text = reset
        sticky = nsew
        row = 2
        column = 1
    .

'''

def printIter(iterable, indent=''):
    '''
    "Pass-through" iterable prints each item as it's yielded.
    '''
    for n in iterable:
        print indent + repr(n)
        yield n

tokens = Scanner().tokenize(source)
tokens = printIter(tokens)

asts = Parser().parse(tokens)
asts = printIter(asts, '    ')

macros = asts.next()
print 'macros:', macros

ets = Formatter(macros).convert(asts)
ets = printIter(ets, '        ')

print list(ets)


## Prints:
##
##    <Tok symbol, mickey>
##    <Tok =, EQ>
##    <Tok symbol, minnie>
##    <Tok symbol, larry>
##    <Tok =, EQ>
##    <Tok symbol, moe>
##    <Tok symbol, text>
##    <Tok symbol, width>
##    <Tok =, EQ>
##    <Tok symbol, 20>
##    <Tok symbol, height>
##    <Tok =, EQ>
##    <Tok symbol, 10>
##    <Tok symbol, sticky>
##    <Tok =, EQ>
##    <Tok symbol, nsew>
##    <Tok symbol, row>
##    <Tok =, EQ>
##    <Tok symbol, 1>
##    <Tok symbol, rowspan>
##    <Tok =, EQ>
##    <Tok symbol, 2>
##    <Tok ., STOP>
##        [<AST 'EQ' None ('mickey', 'minnie') 0 0>, <AST 'EQ' None ('larry', 'moe') 0 0>]
##    macros: [<AST 'EQ' None ('mickey', 'minnie') 0 0>, <AST 'EQ' None ('larry', 'moe') 0 0>]
##        <AST 'EL' None 'text' 0 5>
##            <Element text at -499c87f4>
##    <Tok symbol, frame>
##    <Tok symbol, button>
##    <Tok symbol, text>
##    <Tok =, EQ>
##    <Tok symbol, plot>
##    <Tok symbol, <Button-1>>
##    <Tok =, EQ>
##    <Tok symbol, plotCallback>
##    <Tok ., STOP>
##    <Tok symbol, button>
##    <Tok symbol, sticky>
##    <Tok =, EQ>
##    <Tok symbol, nsew>
##    <Tok symbol, row>
##    <Tok =, EQ>
##    <Tok symbol, 1>
##    <Tok symbol, column>
##    <Tok =, EQ>
##    <Tok symbol, 1>
##    <Tok ., STOP>
##    <Tok ., STOP>
##        <AST 'EL' None 'frame' 2 0>
##            <Element frame at -4911af54>
##    <Tok symbol, button>
##    <Tok symbol, text>
##    <Tok =, EQ>
##    <Tok symbol, reset>
##    <Tok symbol, sticky>
##    <Tok =, EQ>
##    <Tok symbol, nsew>
##    <Tok symbol, row>
##    <Tok =, EQ>
##    <Tok symbol, 2>
##    <Tok symbol, column>
##    <Tok =, EQ>
##    <Tok symbol, 1>
##    <Tok ., STOP>
##        <AST 'EL' None 'button' 0 4>
##            <Element button at -499bf2f4>
##    [<Element text at -499c87f4>, <Element frame at -4911af54>, <Element button at -499bf2f4>]
