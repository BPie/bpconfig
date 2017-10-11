#encoding = utf-8
from __future__ import absolute_import

import os
from operator import getitem
from blessings import Terminal

from . import properties as props


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

    def _print_bar(self):
        with self._t.location(0,0):
            tail = self._pos[:-1]
            head = self._pos[-1]
            print self._t.black_on_white('/'.join(tail)) \
                    + self._t.bold_magenta_on_white('/'+head)

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
            a = raw_input()

    def _clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')

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

