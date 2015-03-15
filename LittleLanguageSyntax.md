# Summary #
```
widgets ::= [macros] element+

element ::= widget_type [options] [element+] .

options ::= equate+
macros ::= equate+

equate ::= something = something
               -or-
           something = "some string"
```

# Details #

  * a widget spec consists of an optional set of **macros** and one or more child **elements**
  * an **element** consists of:
    * a **widget\_type** (one of the Tkinter standard widgets, i.e. Text, Label, Button, etc...)
    * an optional set of **options** for the widget.
    * an optional set of child **elements** for the widget (this only makes sense for Frame widgets though.)
    * a trailing dot **.**
  * both **options** and **macros** consist of one or more **equates**
  * **equates** are either:
    * _thing = thing_
    * _thing = "quoted string"_

## Additionally ##
**widget\_types** are case-INsensitive;  **macros** are substituted for values of **equates** in each **element**; whitespace is not syntactically significant, you can indent your text as you like, you can even put things all on one line...

Any [options from the grid layout manager](http://infohost.nmt.edu/tcc/help/pubs/tkinter/grid.html) can be included and they'll be picked out and applied to the widget's gridding.

See the demos (included in the source) for more info.