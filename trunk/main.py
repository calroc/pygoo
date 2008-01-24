from Tkinter import Tk, Toplevel, Frame
from toXML import toXML
from xml2Tkinter import realize


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


def windowFromSource(source, parent=None, namespace=None):
    if parent is None:
        top = Tk()
    else:
        top = Toplevel(parent)
    F = Frame(top)
    F.grid(sticky='nsew')
    for widget in toXML(source):
        realize(F, widget, d)
    return top


def plotCallback(event):
    print event


d = {'plotCallback': plotCallback}
widget = windowFromSource(source, namespace=d)
print d

widget.mainloop()
