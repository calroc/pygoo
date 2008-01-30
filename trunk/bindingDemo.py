#!/usr/bin/env python
'''
Demonstrates how to use the auto-binding feature of the realize() function.

You can include Tkinter event binding specs in a widget's description that
point to functors in the namespace mapping you pass into realize().  The
resulting widgets will automatically get those events bound to those
functors.  This gives you a quick way to connect your widgets to your
callbacks.

Note that currently including these event specs, with their angle-brackets,
in a widget spec causes ElementTree to emit invalid XML if you convert an
ElementTree element to text.  This will be fixed in a future version.
(If it's bothering you now, feel free to ask me to fix it sooner. -sf)

'''
from Tkinter import Tk, Frame
from pygoo import toXML, realize


class Form:

    widgets = '''

        text
            name = texty
            width = 20
            height = 10

            <Enter> = RedCallback
            <Leave> = GreenCallback

            sticky = nsew
            row = 1
            rowspan = 2
        .
        button
            text = Red
            <Button-1> = RedCallback
            sticky = nsew
            row = 1
            column = 1
        .
        button
            text = Green
            <Button-1> = GreenCallback
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

    def __init__(self, master):

        # Create a "home" widget to build your generated widgets within.
        # (You could also use Toplevel in lieu of Frame.)
        self.frame = Frame(master)
        self.frame.grid(sticky='nsew')

        # Create a namespace dict for realize().
        namespace = dict(
            RedCallback = self.RedCallback,
            GreenCallback = self.GreenCallback,
            )

        # Remember what was already in there for later.
        had = set(namespace)

        # Generate the widgets.
        for widget in toXML(self.widgets):
            realize(self.frame, widget, namespace)

        # Iterate over the new named widgets in the namespace and attach
        # them to self so that the callback methods can "reach" them.
        # (Note that we take out the original callback functors.)
        for new_thing in set(namespace) - had:
            setattr(self, new_thing, namespace[new_thing])

    def RedCallback(self, event):
        '''
        Turn the text widget red.
        '''
        self.texty['background'] = 'red'

    def GreenCallback(self, event):
        '''
        Turn the text widget green.
        '''
        self.texty['background'] = 'green'


root = Tk()
root.title("Binding Demo")

F = Form(root)

root.mainloop()
