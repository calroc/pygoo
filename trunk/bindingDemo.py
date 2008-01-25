#!/usr/bin/env python
from Tkinter import Tk, Frame
from pygoo import toXML, realize


class Form:

    widgets = '''

        text
            name = texty
            width = 20
            height = 10

            <Enter> = Red
            <Leave> = Green

            sticky = nsew
            row = 1
            rowspan = 2
        .
        button
            text = Red
            <Button-1> = Red
            sticky = nsew
            row = 1
            column = 1
        .
        button
            text = Green
            <Button-1> = Green
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
        self.frame = Frame(master)
        self.frame.grid(sticky='nsew')
        self._createWidgets()

    def _createWidgets(self):
        namespace = _getAttributes(self)
        had = set(namespace)

        for widget in toXML(self.widgets):
            realize(self.frame, widget, namespace)

        for new_thing in set(namespace) - had:
            setattr(self, new_thing, namespace[new_thing])

    def Red(self, event):
        self.texty['background'] = 'red'

    def Green(self, event):
        self.texty['background'] = 'green'


def _getAttributes(thing):
    return dict(
        (key, getattr(thing, key))
        for key in dir(thing)
        if not key.startswith('_')
        )


root = Tk()
root.title("Binding Demo")

F = Form(root)

root.mainloop()
