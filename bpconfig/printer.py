#encoding = utf-8
from __future__ import absolute_import
from __future__ import print_function

import sys
import re
from collections import OrderedDict, defaultdict, deque
from operator import getitem
from blessed import Terminal

from . import properties as props
from . import style

class Printer:
    def __init__(self, terminal):
        self._t = terminal
        self._style = style.StyleFactory(self._t)
        self._displaied_attrs = defaultdict( lambda: False, {
            'type': True,
            'name': True,
            'short': True,
            'value': True})
        self._loc_cache = {}


    ''' Marks (highlights) short(cut) in a given name'''
    def _mark_short_in_name(self, name, short, f=None):
        # default formatter
        if not f:
            f = self._t.cyan

        # need to add info about short if not found in name
        if not re.findall(short, name, flags=re.IGNORECASE):
            name = '[{}]: '.format(short) + name
        return re.sub(short, f(short), name, 1, re.IGNORECASE)
        # return name.lower().replace(short.lower(), f(short), 1)

    def _print(self):
        self._clear()
        self._print_header()
        self._print_current()
        self._print_footer()
        deb(self._inp)
        deb(self._spc)
        deb('')

    def _clear(self):
        print(self._t.clear())

    def _print_footer(self):
        th = self._t.height
        prompt = ' >>> {}'.format(self._inp)
        msgs = {
                th: prompt,
                th-1: ' ',
                th-2: '_'*self._t.width,
                th-3: self._info
                }

        for h, msg in msgs.iteritems():
            with self._t.location(0, h):
                print(msg, end='')
                if msg == prompt:
                    x = self._current_loc[1]
                    y = self._current_loc[0]
                    self._loc_cache['prompt'] = x, y

    def _print_current(self):
        if self._state in ('container', 'enum'):
            self._print_options()
        elif self._state == 'property':
            self._print_edit()

    def _print_options(self):
        assert self._state == 'container'
        with self._t.location(0,2):
            print(self._t.center(' ~~~< options >~~~ '))
            for short, cell in self._options.iteritems():
                self._print_option(cell, short)

    def _print_edit(self):
        assert self._state == 'property'
        with self._t.location(0,2):
            print(self._t.center(' ~~~< edit >~~~ '))
            for short, cell in self._parent_options.iteritems():
                if cell == self._current:
                    formatter = None
                else:
                    formatter = self._t.dim
                self._print_option(cell, short, formatter)

    ''' Returns styled string for given cell's attribute.
    Returns empty string if attrname is not found in _displaied_attrs dict.
    '''
    def _get_styled_attr(self, cell, attrname, str_template):
        if not self._displaied_attrs[attrname] or not hasattr(cell, attrname):
            return ''

        attr_val = getattr(cell, attrname)
        filled_str = str_template.format(attr_val)
        styled_str = self._style(cell, attrname)(filled_str)
        return styled_str

    def _print_header(self):
        with self._t.location(0,0):
            tail = self._pos[:-1]
            head = self._pos[-1]
            print(self._t.center(self._t.black_on_white('/'.join(tail))
                    + self._t.bold_black_on_white('/'+head)))
    def _print_option(self, cell, short, style=None):
        msg = ''
        attrstr = lambda n,t: self._get_styled_attr(cell, n, t)
        name = attrstr('name', '{}')
        marked = self._mark_short_in_name(name, short)
        msg += self._t.rjust(attrstr('type', '[{}] '), width=15)
        msg += self._t.center(marked, width=10)
        msg += self._t.ljust(attrstr('value', '= {}'), width=15)

        if style is None:
            style = self._style()
        print(style(self._t.center(msg)))
