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
PROCESSES = []

def close_all_processes():
    for proc in PROCESSES:
        proc.kill()


class Debug:
    def __init__(self, path=PIPE_PATH):
        self._path = path

        if not os.path.exists(self._path):
            os.mkfifo(self._path)

    def show_window(self):
        proc = Popen(['xterm', '-e', 'tail -f %s' % self._path])
        PROCESSES.append(proc)


    def msg(self, message):

        with open(self._path, 'w') as p:
            p.write('{}\n'.format(message))

