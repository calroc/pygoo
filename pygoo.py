'''
pygoo.py - Render a widget spec to Tkinter widgets.

    Copyright (C) 2008 Simon Forman.

    pygoo is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, see <http://www.gnu.org/licenses/>.

'''
import Tkinter
from spark import GenericScanner, GenericParser
try:
    import xml.etree.ElementTree as ET
except ImportError:
    import elementtree.ElementTree as ET

E = ET.Element
S = ET.SubElement


#########################################################################
## Scanner
#########################################################################


class Token:
    def __init__(self, type_, attr, begin, end):
        self.type = type_
        self.attr = attr
        self.begin = begin
        self.end = end

    def __cmp__(self, o):
        return cmp(self.type, o)

    def __hash__(self):
        return hash((self.type, self.attr, self.begin, self.end, id(self)))

    def __repr__(self):
        return '<Tok %s, %s>' % (self.type, self.attr)


class Scanner(GenericScanner):
    ops = {
        '=': 'EQ',
        ':': 'EL',
        '.': 'STOP',
        }
    
    def tokenize(self, input_):
        pos = 0
        n = len(input_)
        while pos < n:

            m = self.re.match(input_, pos)
            if m is None:
                self.error(input_, pos)

            for i, group in enumerate(m.groups()):

                if not group:
                    continue

                try:
                    func = self.index2func[i]
                except KeyError:
                    continue

                begin, end = m.span()

                tok = func(group, begin, end)
                if tok:
                    yield tok

            pos = end

    def t_whitespace(self, s, begin, end):
        r'\s+ '
        pass

    def t_op(self, s, begin, end):
        r'[=.]'
        return Token(s, self.ops[s], begin, end)

    def t_symbol(self, s, begin, end):
        r'[^=.\s]+'
        return Token('symbol', s, begin, end)

    def t_string(self, s, begin, end):
        r'"(.*?)(?<!\\)"'
        assert s.startswith('"') and s.endswith('"')
        s = s[1:-1]
        return Token('string', s, begin, end)


#########################################################################
## Parser
#########################################################################


class AST:
    def __init__(self, type_, tag, els=None, eqs=None, tokens=None):
        self.type = type_
        self.tag = tag
        self.els = els or []
        self.eqs = eqs or []
        self.tokens = tokens and set(tokens) or set()
        self.parent = None
        for ast in self.els:
            if not ast.parent is None:
                raise Exception(('ast already has parent!', ast))
            ast.parent = self

    def __getitem__(self, i): return self.eqs[i]

    def __repr__(self):
        parent = self.parent and self.parent.tag
        return '<AST %s %s %s %s %s>' % tuple(
            repr(n) for n in (
                self.type, parent, self.tag, len(self.els), len(self.eqs)
                )
            )


class ParseError(Exception):
    pass


class Parser(GenericParser):

    def __init__(self, start='begin'):
        GenericParser.__init__(self, start)

    def iterparse(self, tokens):
        tokens = iter(tokens)
        accumulator = []

        for token in tokens:
            accumulator.append(token)
            try:
                macros, elements = GenericParser.parse(self, accumulator)
            except ParseError:
                continue
            yield macros
            if elements:
                yield elements[0]
            break

        accumulator = []
        for token in tokens:
            accumulator.append(token)
            try:
                macros, elements = GenericParser.parse(self, accumulator)
            except ParseError:
                continue
            yield elements[0]
            accumulator = []

        if accumulator:
            raise ParseError("Leftover tokens: %s" % accumulator)

    def error(self, token):
        raise ParseError("Syntax error at or near `%s' token" % token)

    def p_begin(self, args):
        '''
            begin ::= eqlist ellist
            begin ::= ellist
        '''
        if len(args) == 1:
            return [[], args[0]]
        return args

    def p_ellist(self, args):
        '''
            ellist ::= ellist el
            ellist ::= el
        '''
        return self._enlist(args)

    def p_eq(self, args):
        '''
            eq ::= symbol = string
            eq ::= symbol = symbol
        '''
        tokens = self._collectTokens(args)
        KEY, _, VALUE = args
        return AST('EQ', (KEY.attr, VALUE.attr), tokens=tokens)

    def p_eqlist(self, args):
        '''
            eqlist ::= eqlist eq
            eqlist ::= eq
        '''
        return self._enlist(args)

    def p_el(self, args):
        '''
            el ::= symbol .
            el ::= symbol eqlist .
            el ::= symbol ellist .
            el ::= symbol eqlist ellist .
        '''
        tokens = self._collectTokens(args)

        el, stop = args[0], args.pop()

        n = len(args)

        if n == 1:
            EQs, ELs = [], []

        elif n == 2:
            a_list = args[1]
            kind = a_list[0].type

            if kind == 'EQ':
                EQs, ELs = a_list, []

            elif kind == 'EL':
                EQs, ELs = [], a_list
        else:
            EQs, ELs = args[1:]

        return AST('EL', el.attr, ELs, EQs, tokens)

    def _enlist(self, args):
        if len(args) == 1:
            return args
        L, thing = args
        L.append(thing)
        return L

    def _collectTokens(self, args):
        tokens = set()
        for thing in args:
            if isinstance(thing, Token):
                tokens.add(thing)

            elif isinstance(thing, AST):
                tokens.update(thing.tokens)

            elif isinstance(thing, list):
                tokens.update(self._collectTokens(thing))

            else:
                raise TypeError(thing)
        return tokens


#########################################################################
## Convert Parsed ASTs into ElementTree objects.
#########################################################################


class Formatter:

    _GRID_SETTINGS = set('''
        sticky
        ipadx ipady
        padx pady
        row column
        rowspan columnspan
        '''.split())

    def __init__(self, macros):
        self.macros = dict(eq.tag for eq in macros)
        self.parent = None

    def convert(self, elements):
        for el in elements:
            yield self.el(el)

    def el(self, node):
        parent = self.parent

        if parent is None:
            e = E(node.tag)
        else:
            e = S(parent, node.tag)

        self.parent = e
        e.ast = node

        for eq in node.eqs:
            self.eq(eq)
        for el in node.els:
            self.el(el)

        self.parent = parent

        return e

    def eq(self, node):
        key, value = node.tag
        value = self.macros.get(value, value)

        if key in self._GRID_SETTINGS:
            # parent is not None, 'cause eq's outside an el are macros.
            grid = self.parent.find('grid')
            if grid is None:
                grid = S(self.parent, 'grid')
            D = grid.attrib

        else:
            D = self.parent.attrib
        D[key] = value


def toXML(source):
    tokens = Scanner().tokenize(source)
    tokens = list(tokens)
    macros, elements = Parser().parse(tokens)
    return list(Formatter(macros).convert(elements))


#########################################################################
## Convert ElementTree elements into Tkinter widgets.
#########################################################################


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

    bindings, options = _getBindingsAndOptions(element.attrib, namespace)
    name = element.get('name')
    grid = None

    if element.tag.lower() == "frame":

        widget = Tkinter.Frame(master, **options)

        for subelement in element:

            if subelement.tag.lower() == "grid":
                grid = subelement
                continue

            realize(widget, subelement, namespace)

    else:
        if element:

            D = dict((n.tag.lower(), n) for n in element)

            grid = D.pop('grid', None)

            _merge_subelements_to_options(D.values(), options)

        widget_factory = getattr(Tkinter, element.tag.capitalize())

        widget = widget_factory(master, **options)

    if name: namespace[name] = widget

    for event_specifier, callback in bindings.iteritems():
        widget.bind(event_specifier, callback)

    _grid(widget, grid)

    return widget


def _getBindingsAndOptions(options, namespace):
    bindings, settings = {}, {}
    for key, value in options.iteritems():
        if key.startswith('<') and key.endswith('>'):
            try:
                bindings[key] = namespace[value]
            except KeyError:
##                print 'bad binding: %s := %s' % (key, value)
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
