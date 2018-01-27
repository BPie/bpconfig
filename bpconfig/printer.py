#encoding=utf-8
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
    def __init__(self, terminal, debug=None):
        self._t = terminal
        self._style = style.StyleFactory(self._t)
        self._displaied_attrs = defaultdict( lambda: False, {
            'type': True,
            'name': True,
            'short': True,
            'value': True})
        self._loc_cache = {}
        self._debug = debug

    def __call__(self, state, input_handler):
        self._clear()
        self._print_header(state)
        self._print_current(state)
        self._print_footer(input_handler.input_value)

    ''' Marks (highlights) short(cut) in a given name'''
    def _mark_short_in_name(self, name, short, f=None):
        # default formatter
        if not f:
            f = self._t.cyan

        # need to add info about short if not found in name
        if not re.findall(short, name, flags=re.IGNORECASE):
            name = '[{}]: '.format(short) + name

        return re.sub(short, f(short), name, 1, re.IGNORECASE)

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

    @property
    def _current_loc(self):
        return self._t.get_location()

    ''' Prints a footer. '''
    def _print_footer(self, input_value, prefix_msg=''):
        th = self._t.height
        prompt = '{} >>> {}'.format(prefix_msg, input_value)
        msgs = {
                th: prompt,
                th-1: ' ',
                th-2: '_'*self._t.width,
                # th-3: self._info
                }

        for h, msg in msgs.iteritems():
            with self._t.location(0, h):
                print(msg, end='')
                if msg == prompt:
                    x = self._current_loc[1]
                    y = self._current_loc[0]
                    self._loc_cache['prompt'] = x, y

    def _print_current(self, state):
        if state.mode in ('container', 'enum'):
            self._print_options(state)
        elif state.mode in ('property',):
            self._print_edit(state)
        elif state.mode in ('action',):
            pass
        else:
            raise RuntimeError('wrong state: {}'.format(state))

    def _print_options(self, state):
        if state.mode not in ('container', 'enum'):
            raise RuntimeError('wrong state {}'.format(state))

        with self._t.location(0, 2):
            print(self._t.center(' ~~~< options >~~~ '))
            for short, cell in state.options.iteritems():
                self._print_option(cell, short)

    def _print_edit(self, state):
        assert state.mode == 'property'

        with self._t.location(0,2):
            print(self._t.center(' ~~~< edit >~~~ '))
            self._print_option(state.current, '>>')
            # for short, cell in self._parent_options.iteritems():
            #     if cell == self._current:
            #         formatter = None
            #     else:
            #         formatter = self._t.dim
            #     self._print_option(cell, short, formatter)

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

    def _print_header(self, state):
        with self._t.location(0,0):
            tail = state.path[:-1]
            head = state.path[-1]
            print(self._t.center(self._t.black_on_white('/'.join(tail))
                    + self._t.bold_black_on_white('/'+head)))

    def _print_option(self, cell, short, style=None):
        msg = ''
        attrstr = lambda n,t: self._get_styled_attr(cell, n, t)
        marked = self._mark_short_in_name(cell.name, short)
        msg += self._t.rjust(attrstr('type', '[{}] '), width=15)
        msg += self._t.center(marked, width=10)
        msg += self._t.ljust(attrstr('value', '= {}'), width=15)

        if style is None:
            style = self._style()
        print(style(self._t.center(msg)))
