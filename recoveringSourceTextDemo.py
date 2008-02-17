#!/usr/bin/env python
'''
This script shows how to access the AST node of an ElementTree object,
then the Tokens that contributed to that AST, and finally the original
text of the ET's spec in the source string.
'''
from pygoo import Scanner, Parser, Formatter


source = '''

text
    width = 20
    height = 10
    sticky = nsew
    row = 1
    rowspan = 2
.

button
    text = plot
    <Button-1> = plotCallback
    sticky = nsew
    row = 1
    column = 1
.

button
    text = reset
    sticky = nsew
    row = 2
    column = 1
.

label
    text = "A Simple Demo Widget"
    sticky = nsew
    row = 0
    columnspan = 2
.
'''


tokens = list(Scanner().tokenize(source))
macros, asts = Parser().parse(tokens)
ets = Formatter(macros).convert(asts)


for et in ets:

    # tokens attribute is a set.
    tokens = sorted(et.ast.tokens, key=lambda tok: tok.begin)

    begin, end = tokens[0].begin, tokens[-1].end
    print source[begin:end]
    print

    for token in tokens:
        print source[token.begin:token.end],
    print
    print
