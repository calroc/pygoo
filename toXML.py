#!/usr/bin/env python
'''

XML generator script.

'''
from spark import GenericScanner, GenericParser, GenericASTTraversal
from elementtree.ElementTree import Element as E
from elementtree.ElementTree import SubElement as S


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
        r'[=:.]'
        return Token(s, self.ops[s], begin, end)
        
    def t_symbol(self, s, begin, end):
        r'[^=.\s]+'
        return Token('symbol', s, begin, end)
        
    def t_string(self, s, begin, end):
        r'"(.*?)(?<!\\)"'
        assert s.startswith('"') and s.endswith('"')
        s = s[1:-1]
        return Token('string', s, begin, end)


class Parser(GenericParser):
    def __init__(self, start='begin'):
        GenericParser.__init__(self, start)

    def p_begin(self, args):
        '''
            begin ::= eqlist ellist
            begin ::= ellist
            ellist ::= ellist el
            ellist ::= el
        '''
        n = len(args)

        if n == 1:
            n = args[0]
            if isinstance(n, list):
                return [[], n]
            return args

        elif n == 2:
            head, tail = args
            if isinstance(tail, list):
                return args
            head.append(tail)
            return head

    def p_eq(self, args):
        '''
            eq ::= symbol = string
            eq ::= symbol = symbol
        '''
        tokens = _collectTokens(args)
        KEY, _, VALUE = args
        return AST('EQ', (KEY.attr, VALUE.attr), tokens=tokens)

    def p_eqlist(self, args):
        '''
            eqlist ::= eqlist eq
            eqlist ::= eq
        '''
        n = len(args)

        if n == 1:
            return args

        if n == 2:
            head, tail = args
            head.append(tail)
            return head

    def p_el(self, args):
        '''
            el ::= symbol .
            el ::= symbol eqlist .
            el ::= symbol ellist .
            el ::= symbol eqlist ellist .
        '''
        tokens = _collectTokens(args)

        el, stop = args[0], args.pop()
        assert stop.attr == 'STOP', stop

        n = len(args)

        if n == 1:
            EQs, ELs = [], []

        elif n == 2:
            something = args[1]
            assert something, repr(something)

            if something[0].type == 'EQ':
                EQs, ELs = something, []

            elif something[0].type == 'EL':
                EQs, ELs = [], something

            else:
                raise ValueError(something)

        elif n == 3:
            EQs, ELs = args[1:]

        else:
            raise 'heck', n

        return AST('EL', el.attr, ELs, EQs, tokens)


def _collectTokens(args):
    tokens = set()
    for thing in args:
        if isinstance(thing, Token):
            tokens.add(thing)

        elif isinstance(thing, AST):
            tokens.update(thing.tokens)

        elif isinstance(thing, list):
            tokens.update(_collectTokens(thing))

        else:
            raise TypeError(thing)
    return tokens


##############################
## Convert Parsed ASTs into ElementTree objects.
##

##    class ToXMLTraversal(GenericASTTraversal):
##        def __init__(self, ast):
##            GenericASTTraversal.__init__(self, ast)
##            self.postorder()
##
##        def n_EL(self, node):
##            print node
##
##        def n_EQ(self, node):
##            print node


def eqs2dict(eqs, subs={}):
    '''
    convert a list of EQs to a dict, mapping the values through the macros
    if appropriate.
    '''
    if not eqs:
        return {}
    res = {}
    for eq in eqs:
        key, value = eq.tag
        value = subs.get(value, value)
        res[key] = value
    return res


_GRID_SETTINGS = set('sticky row column rowspan columnspan'.split())


def createElement(parent, el, macros):
    widget_type = el.tag
    children = el.els
    attributes = eqs2dict(el.eqs, macros)

    # Extract grid settings if any...
    grid_settings = {}
    for key in _GRID_SETTINGS:
        try:
            value = attributes.pop(key)
        except KeyError:
            continue
        grid_settings[key] = value

    if parent is None:
        e = E(widget_type, attrib=attributes)
    else:
        e = S(parent, widget_type, attrib=attributes)

    if grid_settings:
        S(e, 'grid', attrib=grid_settings)

    for kid in children:
        createElement(e, kid, macros)

    return e
            
        
def ast2elementtree(macros, elements):
    macros = dict(eq.tag for eq in macros)
    return [createElement(None, el, macros) for el in elements]


def toXML(source):
    tokens = list(Scanner().tokenize(source))
    macros, elements = Parser().parse(tokens)
    return ast2elementtree(macros, elements)


if __name__ == '__main__':

    source = '''

    WIDTH = 23

    label
        text = "Hey there"
        width = WIDTH
        sticky = w
        .
    entry
        width = WIDTH
        sticky = w
        .
    '''


    s = Scanner()
    t = list(s.tokenize(source))
    print t
    p = Parser()
    macros, elements = p.parse(t)
    print macros
    print elements
