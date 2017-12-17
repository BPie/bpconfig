#encoding = utf-8
from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import re

from collections import OrderedDict, defaultdict, deque
from operator import getitem
from blessed import Terminal
from subprocess import Popen

from . import properties as props
from . import style


PIPE_PATH = '/tmp/my_pipe'

class Debug:
    def __init__(self, path=PIPE_PATH):
        self._path = path

        if not os.path.exists(self._path):
            os.mkfifo(self._path)

        Popen(['xterm', '-e', 'tail -f %s' % self._path])

    def msg(self, message):
        with open(self._path, 'w') as p:
            p.write('{}\n'.format(message))

