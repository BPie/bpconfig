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


class ActionManager(object):

    def __init__(self, debug=None):
        self._actions = {}
        self._debug = debug

    def add(self, key, action):
        if key in self._actions.keys():
            raise KeyError('key {} already in use for '
                    .format(key, self._actions[key].name))
        self._actions[key] = action

    @property
    def all(self):
        return self._actions

    @property
    def usable(self):
        return {key: action for (key, action) in self._actions.iteritems() if action}

    def __getitem__(self, key):
        return self.usable[key]

