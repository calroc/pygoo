'''
xml2Tkinter.py - Render an XML description to Tkinter widgets.

    Copyright (C) 2006, 2007 Simon Forman.

    xml2Tkinter is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA


This module is based on a function written by Fredrik Lundh (aka "the
Effbot") that converts XML (as an elementtree element) into Tkinter
widgets[1].  I modified it to notice and apply grid layout manager
options, and to register wigets with name attributes in a namespace
object.


Module exports one function:

    realize(master, element, namespace=None)

        master - Tkinter container widget to use as this widget's parent.

        element - ElementTree Element describing the desired widget.

        namespace - [Optional] a namespace to bind child widgets to, if
            their 'name' attribute is specified in the element XML.

            (Hint: pass an object's __dict__ to have widgets available as
            attributes of that object.  See the example below.)

 
[1] "Generating Tkinter User Interfaces from XML"
http://effbot.org/zone/element-tkinter.htm

'''
import Tkinter
try:
    from xml.etree.ElementTree import XML
except ImportError:
    from elementtree.ElementTree import XML


def realize(master, element, namespace=None):
    '''
    Grok XML description into actual widgets.

    master - Tkinter container widget to use as this widget's parent.
    element - ElementTree Element describing the desired widget.
    namespace - [Optional] a namespace to bind child widgets to, if their
        'name' attribute is specified in the element XML.  (Hint: pass a
        class's __dict__ object to have widgets available as attributes
        of their instance.  See the example below.)
    '''

    if namespace is None:
        namespace = {}

    if element.tag.lower() == "frame":

        B, O = _getBindingsAndSettings(element.attrib, namespace)

        frame = Tkinter.Frame(master, **O)

        name = element.get('name')
        if name:
            namespace[name] = frame

        grid = None
        for subelement in element:

            if subelement.tag.lower() == "grid":
                grid = subelement
                continue

            realize(frame, subelement, namespace)

        _grid(frame, grid)

        widget = frame

    else:
        widget_factory = getattr(Tkinter, element.tag.capitalize())

        B, options = _getBindingsAndSettings(element.attrib, namespace)

        if element:

            D = dict((n.tag.lower(), n) for n in element)

            grid = D.pop('grid', None)

            _merge_subelements_to_options(D.values(), options)

        else:
            grid = None

        widget = widget_factory(master, **options)

        name = element.get('name')
        if name:
            namespace[name] = widget

        _grid(widget, grid)

        for event_specifier, callback in B.iteritems():
            widget.bind(event_specifier, callback)

    return widget


def _getBindingsAndSettings(options, namespace):
    bindings, settings = {}, {}
    for key, value in options.iteritems():
        if key.startswith('<') and key.endswith('>'):
            try:
                bindings[key] = namespace[value]
            except KeyError:
                print 'bad binding: %s := %s' % (key, value)
                continue
        else:
            settings[key] = value
    return bindings, settings


def _grid(widget, element):
    '''
    Collect grid options from element and use them to place the widget
    using the 'grid' layout manager.
    '''

    if element is None:
        options = {}

    else:
        options = element.attrib.copy()
        _merge_subelements_to_options(element, options)

    widget.grid(**options)


def _merge_subelements_to_options(iterable, options):
    '''
    Merge attributes in subelements into an options dictionary.
    '''
    for subelement in iterable:
        options[subelement.tag] = subelement.text


if __name__ == '__main__':
    from Tkinter import Tk

    class Form:

        form = XML("""\
        <Frame>
            <label>
                <text>entry:</text>
                <grid sticky='e'/>
            </label>

            <entry name='entry' width='30' bg='gold'>
                <grid column='1' row='0' columnspan='2'/>
            </entry>

            <checkbutton><text>checkbutton</text>
                <grid column='1' sticky='nesw'/>
            </checkbutton>

            <button name='ok' text='OK' width='10'>
                <grid row='2' sticky='nesw'/>
            </button>

            <button name='cancel' text='Cancel' width='10'>
                <grid row='2' column='2' sticky='nesw'/>
            </button>
        </Frame>
            """)

        def __init__(self, master):
            self.frame = realize(master, self.form, self.__dict__)
            self.grid = self.frame.grid

            # add button behaviour
            self.ok.config(command=self.Ok)
            self.cancel.config(command=self.Quit)

        def Quit(self):
            self.frame.destroy()
            self.frame._root().quit()

        def Ok(self):
            print self.entry.get()
            self.Quit()

    root = Tk()
    root.title("ElementTk")

    F = Form(root)
    F.grid()

    root.mainloop()
