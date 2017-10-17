#encoding = utf-8
from __future__ import absolute_import

import os
from collections import OrderedDict
from operator import getitem
from blessings import Terminal

from . import properties as props

def fingerprint_finder(names, mapped_fingerprint=None, generator=None):
    current_name = names[0]
    if not mapped_fingerprint:
        mapped_fingerprint = OrderedDict()
    used = mapped_fingerprint.keys()
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
            fingerprint = next(generator)
            while fingerprint in used:
                fingerprint = next(generator)
        else:
            fingerprint = possible_upper[0]
    else:
        fingerprint = possible[0]


    names = names[1:]
    mapped_fingerprint[fingerprint] = current_name

    if names:
        mapped_fingerprint = fingerprint_finder(names,
                mapped_fingerprint, generator)

    return mapped_fingerprint

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
        self._flags = {'type': True, 'name': True, 'shortcut': True}

    def _print_bar(self):
        with self._t.location(0,0):
            tail = self._pos[:-1]
            head = self._pos[-1]
            print self._t.black_on_white('/'.join(tail)) \
                    + self._t.bold_black_on_white('/'+head)

    def _print_cell(self, cell, shortcut=None):
        msg = ''
        if self._flags['shortcut'] and shortcut is not None:
            msg += '[{}] '.format(shortcut)

        if self._flags['type']:
            msg += cell.fields['type'] + ': '

        if self._flags['name']:
            msg += cell.fields['name']
        print msg

    def _print_options(self):
        shortcuts = fingerprint_finder(self._current.keys())

        with self._t.location(5, 5):
            print ' ~~~< options >~~~ '
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
            self._up()

    @property
    def _in_root(self):
        return len(self._pos) == 1

    def _go_down(self):
        if self._in_root:
            raise RuntimeWarning('you\'re in root')
        else:
            self._pos = self._pos[:-1]
            self._up()

    def run(self):
        with self._t.fullscreen():
            self._print_bar()
            self._print_options()
            a = raw_input()

    # def _clear(self):
    #     os.system('cls' if os.name == 'nt' else 'clear')

    def _up(self):
        pass
        # self._clear()
        # self.print_all()


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


    # print fingerprint_finder(some_list)


