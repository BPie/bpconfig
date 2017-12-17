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


class State(object):

    def __init__(self, container):
        if isinstance(container, list):
            self._container = props.CellContainer('root', container)
        elif isinstance(container, props.CellContainer):
            self._container = container
        else:
            raise ValueError("Wrong container type")


        self._pos = [self._container.name]
        self._info = ''

    ''' Gets current cell'''
    @property
    def current(self):
        return reduce(getitem, self._pos[1:], self._container)

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
            raise ValueError('wrong current type: {}'.format(self._current))



    ''' Returns boolean if in root '''
    @property
    def in_root(self):
        return len(self._pos) == 1


    ''' Go to next cell (child) with matching name '''
    def go_next(self, name):
        try:
            new_cell = self._current[name]
        except:
            raise RuntimeWarning('wrong child name: {}'.format(name))
        else:
            self._pos.append(new_cell.name)

    ''' Go to previous cell (parent) '''
    def go_previous(self):
        if self._in_root:
            raise RuntimeWarning('you\'re in root')
        else:
            self._pos = self._pos[:-1]

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
