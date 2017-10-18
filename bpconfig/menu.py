#encoding = utf-8
from __future__ import absolute_import
from __future__ import print_function

import os
from collections import OrderedDict, defaultdict
from operator import getitem
from blessed import Terminal

from . import properties as props


def shortcut_finder(names, mapped_shortcut=None, generator=None, banned=None):
    current_name = names[0]
    if not mapped_shortcut:
        mapped_shortcut = OrderedDict()
    used = mapped_shortcut.keys()
    if banned is not None:
        used += banned
    possible = [ch for ch in current_name if ch not in used]

    if not possible:
        possible_upper = [ch.upper() for ch in current_name
                if ch.upper() not in used]

        if not possible_upper:
            if generator is None:
                def gen():
                    i = 0
                    while True:
                        yield '{}'.format(i)
                        i += 1
                generator = gen()

            # while for the case when there were already numbers
            # (eg. there was a cell with name "1something")
            shortcut = next(generator)
            while shortcut in used:
                shortcut = next(generator)
        else:
            shortcut = possible_upper[0]
    else:
        shortcut = possible[0]

    names = names[1:]
    mapped_shortcut[shortcut] = current_name

    if names:
        mapped_shortcut = shortcut_finder(names,
                mapped_shortcut, generator)

    return mapped_shortcut


class Menu(object):

    def __init__(self, container):
        if isinstance(container, list):
            self._container = props.CellContainer('root', container)
        elif isinstance(container, props.CellContainer):
            self._container = container
        else:
            raise ValueError("Wrong container type")


        self._pos = [self._container.name]
        self._t = Terminal()
        self._flags = defaultdict( lambda: False, {
            'type': True,
            'name': True,
            'shortcut': True,
            'value': True})

    def _actions(self, inactive_too=False):
        actions = {}

        if inactive_too or not self._in_root:
            actions['h'] = props.Action('back', lambda: self._go_down())

        return actions

    @property
    def _reserved_shortcuts(self):
        return self._actions(True).keys()


    def _print_headder(self):
        with self._t.location(0,0):
            tail = self._pos[:-1]
            head = self._pos[-1]
            print(self._t.black_on_white('/'.join(tail)) \
                    + self._t.bold_black_on_white('/'+head))


    def _formated_cell_attr(self, cell, attrname, str_template):
        if not self._flags[attrname] or not hasattr(cell, attrname):
            return ''

        attr_val = getattr(cell, attrname)
        return str_template.format(attr_val)

    def _print_cell(self, cell, shortcut=None):
        msg = ''
        attrstr = lambda n,t: self._formated_cell_attr(cell, n, t)
        msg += attrstr('type', '[{}] ')
        msg += attrstr('name', '{}')
        msg += attrstr('value', ' = {}')
        print(msg)

    def _print_options(self):
        banned = self._reserved_shortcuts
        shortcuts = shortcut_finder( self._current.keys(), banned=banned)

        with self._t.location(5, 5):
            print(' ~~~< options >~~~ ')
            for shortcut, cell in zip(shortcuts.keys(), self._current):
                self._print_cell(cell, shortcut)

    @property
    def _current(self):
        return reduce(getitem, self._pos[1:], self._container)

    def _go_up(self, name):
        try:
            new_cell = self._current[name]
        except:
            raise RuntimeWarning('wrong child name: {}'.format(name))
        else:
            self._pos.append(new_cell.name)

    @property
    def _in_root(self):
        return len(self._pos) == 1

    def _go_down(self):
        if self._in_root:
            raise RuntimeWarning('you\'re in root')
        else:
            self._pos = self._pos[:-1]

    def _clear(self):
        print(self._t.clear())

    @property
    def location(self):
        return self._t.get_location(timeout=5)

    def _print_footer_and_interact(self):
        th = self._t.height
        prompt = ' >>> '
        msgs = {
                th: prompt,
                th-1: ' ',
                th-2: '_'*self._t.width,
                }

        for h, msg in msgs.iteritems():
            with self._t.location(0, h):
                if msg == prompt:
                    prompt_loc = self.location
                print(msg, end='')

        w, h = prompt_loc[1], prompt_loc[0]
        w = w + len(prompt)
        # h = h - 2
        with self._t.location(w, h):
            inp = raw_input()
            self._handle_input(inp)

    def _handle_input(self, inp):
        actions = self._actions()
        if inp in actions:
            actions[inp]()
        else:
            pass

    def run(self):
        with self._t.fullscreen():
            while(True):
                self._clear()
                self._print_headder()
                self._print_options()
                self._print_footer_and_interact()  # has to be the last one!


if __name__ == '__main__':
    cont_2 = props.CellContainer('lvl2',
            [props.Cell('2c1'),
            props.Property('2p1', 1),
            props.PropertyString('2p2', 'string')])
    cont_1 = props.CellContainer('lvl1', [props.Cell('1c2'), cont_2])
    cont_root = props.CellContainer('root', [props.Cell('rc1'), cont_1])

    menu = Menu(cont_root)
    menu._go_up('lvl1')
    menu._go_up('lvl2')
    menu.run()
    # menu._print_bar()

    # some_list = [
    #         'name',
    #         'nome',
    #         'far',
    #         'foo',
    #         'bar',
    #         'noob',
    #         'something',
    #         'quant']


    # print(fingerprint_finder(some_list))


