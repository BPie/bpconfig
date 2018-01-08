#encoding = utf-8
from __future__ import absolute_import
from __future__ import print_function

import sys
import re
from collections import OrderedDict, defaultdict, deque
from operator import getitem
from blessed import Terminal

from . import properties as props


'''
class that creates short (shortcut) from given set of Cells.

If possible shorts are letters from cell.name attribute (upper or lowercase).
'''
class ShortMapper:
    def __init__(self):
        pass

    '''
    Creates shorts for given names.

    Shorts are shortcuts (preffered one char).
    If mapped_shorts is not None but a dict, the function expands this dict.
    Generator TODO
    banned is a list of shorts that should not be used.
    '''
    def __call__(self, names, mapped_short=None, generator=None, banned=None):
        current_name = names[0]
        if not mapped_short:
            mapped_short = OrderedDict()
        used = mapped_short.keys()
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
                short = next(generator)
                while short in used:
                    short = next(generator)
            else:
                short = possible_upper[0]
        else:
            short = possible[0]

        names = names[1:]
        mapped_short[short] = current_name

        if names:
            mapped_short = self.__call__(
                    names=names,
                    mapped_short=mapped_short,
                    generator=generator,
                    banned=banned)

        return mapped_short


'''
Class that finds shors matching given sentence
'''
class ShortFinder:

    def __init__(self):
        pass


    REGEXP = { 'exact': r'^{}$',
            'prefixed': r'^{}(\S*)$' }
            # r'^{}(\S+)$'

    def __call__(self, shorts, sequence):
        regex_str = self.REGEXP['prefixed'].format(sequence)

        return [s for s in shorts if re.match(regex_str, s)]

    # not needed for now
    # def contains(self, shorts, sequence):
    #     regex_str = self.REGEXP['exact'].format(sequence)

    #     for s in shorts:
    #         if re.match(regex_str, s):
    #             return True
    #     return False



