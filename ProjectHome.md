Inspired in part by the "LayLa" Layout Language that Jörg Derungs developed for the Oberon system, pygoo is a simple way to transform a Little Language widget specification into Tkinter widgets.

For example, this GUI window:

![http://pygoo.googlecode.com/files/bindingDemo.jpg](http://pygoo.googlecode.com/files/bindingDemo.jpg)

was the result of processing the following LL widget spec:

```
text
    name = texty
    width = 20
    height = 10
    sticky = nsew
    row = 1
    rowspan = 2
.
button
    text = Red
    sticky = nsew
    row = 1
    column = 1
.
button
    text = Green
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
```