#!/usr/bin/env python
'''
A simple demo that shows how to write a function that will produce new
"Toplevel" windows on the fly from a passed in source string.
'''
from Tkinter import Tk, Toplevel
from pygoo import toXML, realize


source = '''
    button
        text = "Click Me!"
        <Button-1> = callback
        sticky = nsew
        row = 1
    .
    button
        text = "I do nothing"
        sticky = nsew
        row = 1
        column = 1
    .
    label
        text = "A Simple Demo Widget"
        sticky = nsew
        row = 0
        columnspan = 2
    .'''


def text2window(source, title, root=None, namespace=None):
    '''
    Convert source to a new Toplevel window using root if given.  The
    namespace is passed to the realize() function.
    '''
    if root is not None:
        # Create a new Toplevel from the passed in root.
        top = Toplevel(root)
    else:
        # Create a brand new Tk interpreter-with-Toplevel.
        top = Tk()

    top.title(title)

    # Realize the widgets.
    for widget in toXML(source):
        realize(top, widget, namespace)

    return top


def callback(event):
    print event
    print repr(event.widget)
    print '----------'


window = text2window(source, "Pygoo Demo", namespace={'callback':callback})
window.mainloop()
