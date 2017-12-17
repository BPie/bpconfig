#encoding = utf-8
from __future__ import absolute_import
from __future__ import print_function

import sys
import re
from collections import OrderedDict, defaultdict, deque
from operator import getitem
from blessed import Terminal

from .state import State
from .printer import Printer
from .input import InputManager
from .shorts import ShortManager
from .actions import ActionManager
from . import properties as props


class Menu(object):
    def __init__(self, container):
        self._t = Terminal()

        self._state = State(container)
        self._print = Printer(self._t)
        self._input = InputManager(self._t)
        self._shorts = ShortManager()
        self._actions = ActionManager()


    ''' Inits actions '''
    def _init_actions(self):

        # go previous
        go_previous_act = props.Action(
                'left',
                lambda: self._go_previous(),
                lambda: not self._in_root)
        self._actions.add_action('h', go_previous_act)

        # go down
        go_down_act = props.Action(
                'down',
                lambda: self._highlight_down(),
                lambda: self._state == 'container')
        self._actions.add_action('j', go_down_action)

        # go up
        go_up_act= props.Action(
                'up',
                lambda: self._highlight_up(),
                lambda: self._state == 'container')
        self._actions.add_action('k', go_up_action)

        # go next
        go_next_act= props.Action(
                'right',
                lambda: self._go_up(self._highlighted),
                lambda: (self._state in ('container', 'enum')
                        and self._highlighted))
        self._actions.add_action('l', go_next_action)

        # cancel
        cancel_act= props.Action(
                'cancel',
                lambda: self._cancel,
                lambda: self._state in ('property', 'enum'))
        self._actions.add_action('KEY_ESCAPE', cancel_act)
        self._actions.add_action('cancel', cancel_act)

        # accept
        accept_act = props.Action(
                'accept',
                lambda: self._accept,
                lambda: self._state in ('container', 'enum'))
        self._actions.add_action('KEY_ENTER', accept_act)
        self._actions.add_action('accept', accept_act)

        # quit
        quit_act = props.Action('quit', lambda: sys.exit())
        self._actions.add_action('Q', quit_act)

    '''
    Gets current possible options

    Excludes used shorst (by actions).
    Returns OrderedDict (shorts: cells)
    '''
    @property
    def _options(self):
        if self._state.mode not in ('enum', 'container'):
            return None

        used_keys = self._actions.all.keys()
        current = self._state.current
        shorts = self._shorts.find(current.keys(), banned=used_keys)

        return OrderedDict(zip(shorts, current.values()))

    def run(self):
        print(self._options)
        # with self._t.fullscreen():
        #     while(True):
        #         self._print()
        #         self._gather_inp()
        #         self._handle_inp()

def _test_get_root():
    cont_2 = props.CellContainer('lvl2',
            [props.Cell('2c1'),
            props.Property('2p1', 1),
            props.PropertyString('2p2', 'string')])
    cont_1 = props.CellContainer('lvl1', [props.Cell('1c2'), cont_2])
    cont_root = props.CellContainer('root', [props.Cell('rc1'), cont_1])
    return cont_root


if __name__ == '__main__':

    root_container = _test_get_root()
    menu = Menu(root_container)
    menu.run()
