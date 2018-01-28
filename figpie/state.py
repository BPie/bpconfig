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
from .shorts import ShortMapper


class State(object):

    def __init__(self, container, actions, debug=None):
        if isinstance(container, list):
            self._container = props.CellContainer('root', container)
        elif isinstance(container, props.CellContainer):
            self._container = container
        else:
            raise ValueError("Wrong container type")


        self._pos = [self._container.name]
        self._info = ''
        self._shorts = ShortMapper()
        self._actions = actions
        self._debug = debug

    @property
    def path(self):
        return self._pos

    ''' Gets current cell'''
    @property
    def current(self):
        # becouse last one can be a cell, we need to make sure we get the item,
        # not it's value due to CellContainer's 'get', so we get it
        # with _ added (check CellContainer.__getitem__)
        return reduce(getitem,
                ('*'+pos for pos in self._pos[1:]),
                self._container)

    ''' Gets current cell's parent'''
    @property
    def parent(self):
        return reduce(getitem, self._pos[1:-1], self._container)

    @property
    def mode(self):
        if isinstance(self.current, props.PropertyEnum):
            return 'enum'
        elif isinstance(self.current, props.Property):
            return 'property'
        elif isinstance(self.current, props.CellContainer):
            return 'container'
        elif isinstance(self.current, props.Action):
            return 'action'
        else:
            raise ValueError('wrong current type: {}'.format(self.current))



    ''' Returns boolean if in root '''
    @property
    def in_root(self):
        return len(self._pos) == 1


    ''' Go to next cell (child) with matching name '''
    def go_next(self, name):
        try:
            new_cell = self.current[name]
        except KeyError:
            raise RuntimeWarning('wrong child name: {}'.format(name))
        else:
            self._pos.append(name)

    ''' Go to previous cell (parent) '''
    def go_previous(self):
        if self.in_root:
            raise RuntimeWarning('you\'re in root')
        else:
            self._pos = self._pos[:-1]

    '''
    Gets current possible options

    Excludes used shorst (by actions).
    Returns OrderedDict (shorts: cells)
    '''
    @property
    def options(self):
        if self.mode not in ('enum', 'container'):
            return None

        used_keys = self._actions.all.keys()
        current = self.current
        short_map = self._shorts(current.keys(), banned=used_keys)

        return OrderedDict(zip(short_map, current.values()))

    '''
    Gets possible actions to invoke

    Returns dict (shorts: actions)
    '''
    @property
    def actions(self):
        return self._actions.usable

    # @property
    # def _current_loc(self):
    #     return self._t.get_location()

    # @property
    # def _parent_options(self):
    #     return self._get_options(self._parent)

    # @property
    # def _highlighted(self):
    #     return None

    # def _highlight_down(self):
    #     pass

    # def _highlight_up(self):
    #     pass
    # @property
    # def _state(self):
    #     if isinstance(self._current, props.PropertyEnum):
    #         return 'enum'
    #     elif isinstance(self._current, props.Property):
    #         return 'property'
    #     elif isinstance(self._current, props.CellContainer):
    #         return 'container'
    #     else:
    #         raise ValueError('wrong current type: {}'.format(self._current))
