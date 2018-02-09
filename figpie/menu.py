#encoding = utf-8
from __future__ import absolute_import
from __future__ import print_function

import sys
import re
import atexit

from collections import OrderedDict, defaultdict, deque
from operator import getitem
from blessed import Terminal

from .state import State
from .printer import Printer
from .input import InputManager
from .shorts import ShortMapper
from .actions import ActionManager

from . import debug as deb
from . import properties as props


class Menu(object):

    def __init__(self, container, debug=False):
        self._t = Terminal()

        if debug:
            self._debug = deb.Debug()
        else:
            self._debug = deb.DummyDebug()

        self._actions = ActionManager(self._debug)
        self._state = State(container, self._actions, self._debug)
        self._init_actions()
        self._printer = Printer(self._t, self._debug)
        self._input = InputManager(self._t, self._debug)


    ''' Inits actions '''
    def _init_actions(self):

        # go previous
        go_previous_act = props.Action(
                'left',
                lambda: self._state.go_previous(),
                lambda: not self._state.in_root)
        self._actions.add('h', go_previous_act)

        # quit
        quit_act = props.Action('quit', self.quit)
        self._actions.add('Q', quit_act)



#         # go down
#         go_down_act = props.Action(
#                 'down',
#                 lambda: self._highlight_down(),
#                 lambda: self._state == 'container')
#         self._actions.add('j', go_down_act)

#         # go up
#         go_up_act= props.Action(
#                 'up',
#                 lambda: self._highlight_up(),
#                 lambda: self._state == 'container')
#         self._actions.add('k', go_up_act)

#         # go next
#         go_next_act= props.Action(
#                 'right',
#                 lambda: self._go_up(self._highlighted),
#                 lambda: (self._state in ('container', 'enum')
#                         and self._highlighted))
#         self._actions.add('l', go_next_act)

#         # cancel
#         cancel_act= props.Action(
#                 'cancel',
#                 lambda: self._cancel,
#                 lambda: self._state in ('property', 'enum'))
#         self._actions.add('KEY_ESCAPE', cancel_act)
#         self._actions.add('cancel', cancel_act)

#         # accept
#         accept_act = props.Action(
#                 'accept',
#                 lambda: self._accept,
#                 lambda: self._state in ('container', 'enum'))
#         self._actions.add('KEY_ENTER', accept_act)
#         self._actions.add('accept', accept_act)

    def quit(self):
        self._debug.msg('quitting...')
        sys.exit()

    def run(self):
        with self._t.fullscreen():
            while(True):
                self._printer(self._state, self._input)
                try:
                    self._input(self._state)
                except (KeyError, props.WrongTypeException,
                        props.WrongValueException,
                        props.WrongNameException) as e:
                    self._state.add_warning(str(e))


def _test_get_root():
    u = props.Union('union', {
        'a': [props.PropertyInt('a1',2), props.PropertyFloat('a2',3.4)],
        'b': [props.PropertyString('b1', 'asdf')]
        })
    cont_2 = props.CellContainer('lvl2',
            [props.PropertyInt('2c1', 234),
            props.Property('2p1', 1),
            props.PropertyString('2p2', 'string'),
            props.PropertyFloat('float prop', 5.2),
            props.PropertyInt('int prop', 5) ,
            props.PropertyEnum('enum prop',
                [props.Cell(e_str) for e_str in ['a', 'b', 'c', 'd']],
                'a'),
            u
            ])
    cont_1 = props.CellContainer('lvl1', [props.Cell('1c2'), cont_2])
    cont_root = props.CellContainer('root', [
            props.Cell('rc1'),
            props.Lambda('lambda', lambda: 1),
            cont_1,
        ])
    return cont_root


if __name__ == '__main__':

    root_container = _test_get_root()
    menu = Menu(root_container, False)
    atexit.register(deb.close_all_processes)

    menu.run()
    # try:
    #     menu.run()
    # except Exception as e:
    #     print('exception occured: ', e)
