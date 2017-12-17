#encoding = utf-8
from __future__ import absolute_import
from __future__ import print_function

import sys
import re
from collections import OrderedDict, defaultdict, deque
from operator import getitem
from blessed import Terminal

from . import properties as props


class InputManager:
    def __init__(self, terminal):
        self._t = terminal
        self._inp = ''
        self._spc = ''
        self._actions = {}


    def add_action(self, key, action):
        self._actions[key] = action

    def _gather_inp(self):
        with self._t.location(*self._loc_cache['prompt']):
            with self._t.cbreak():
                val = self._t.inkey(timeout=1)
                if not val:
                    self._spc = 'timeout'
                elif val.is_sequence and val.name in ('KEY_ENTER', 'KEY_ESCAPE'):
                    self._spc = val.name
                elif len(str(val)) == 1:
                    self._inp += str(val)
                else:
                    self._info = 'unhandled inp character: [{}]'.format(val)

    def _clean_all_inp(self):
        self._clean_inp()
        self._clean_spc()

    def _clean_inp(self):
        self._inp = ''

    def _clean_spc(self):
        self._spc = ''

    def _handle_inp(self):
        self._try_consume_inp()
        # if self._state == 'container':
        #     pass
        # elif self._state == 'property':
        #     pass
        # elif self._state == 'enum':
        #     pass
        # else:
        #     raise ValueError('unsupported mode: {}'.format(self._state))

        # if self._spc_meaning == 'cleaning':
        #     self._info = 'inp cleaned'
        #     self._clean_all_inp()
        # elif len(self._fltr_shorts('all')) <= 0:
        #     self._info = 'wrong inp: [{}]!'.format(self._inp)
        #     self._clean_all_inp()
        # elif len(self._fltr_shorts('all')) == 1 or \
        #          (self._spc_meaning == 'consume' and self._inp):
        #     self._consume_inp()
        #     self._clean_all_inp()
        # else:
        #     add_msg =  r' waiting for inp ...'
        #     if not re.findall(add_msg, self._info):
        #         self._info += ' (' + add_msg + ')'

    def _cancel(self):
        if self._state == 'container':
            self._clean_all_inp()
        elif self._state in ('property', 'enum'):
            self._clean_all_inp()
            self._go_down()
        else:
            raise ValueError('unsupported mode: {}'.format(self._state))

    def _accept(self):
        if not self._try_consume_inp():
            self._cancel()

    def _timeout(self):
        self._try_consume_inp()

    def _try_consume_spc(self, force_clean=False):
        if not self._spc:
            return False

        try:
            self._actions[self._spc]()
        except:
            if force_clean:
                self._clean_spc()
            return False
        else:
            self._clean_spc()
            return True


    def _try_consume_inp(self, force_clean=False):
        if not self._inp:
            return False

        if self._try_consume_inp_as_action(force_clean):
            return True

        if self._try_consume_inp_as_edit(force_clean):
            return True

        return False

    def _try_consume_inp_as_action(self, force_clean=False):
        # proper beginning
        if not self._inp.startswith(':'):
            if force_clean:
                self._clean_inp()
            return False

        # try to get name and execute action with that name
        try:
            name = self._inp[1:]
            self._actions[name]()
        except:
            if force_clean:
                self._clean_inp()
            return False
        else:
            self._clean_inp()
            return True

    def _try_consume_inp_as_edit(self, force_clean=False):
        pass

    def _consume_inp(self):
        # getting the right name for an option or action
        if len(self._fltr_shorts('exact')) == 1:
            short = self._inp
        elif len(self._fltr_shorts('all')) == 1:
            short = self._fltr_shorts('all')[0]
        else:
            self._info += ' (failed: not found)'
            return

        # executing
        if short in self._actions:
            action = self._actions[short]
            self._info = 'invoked action [{}]: {}'.format(short, action.name)
            action()
        elif short in self._options:
            opt = self._options[short]
            self._info = 'option [{}]: {}'.format(short, opt.name)
            self._go_up(opt.name)
        else:
            raise RuntimeError('wrong shortcut ({}) to consume'.format(short))

    def _r_str(self, s, mode):
        if mode == 'exact':
            return r'^{}$'.format(s)
        elif mode == 'all':
            return r'^{}(\S*)$'.format(s)
        elif mode == 'prefix':
            return r'^{}(\S+)$'.format(s)
        else:
            raise ValueError('wong mode value: {}'.format(mode))

    def _fltr_all_actions_short(self, mode):
        r_str = self._r_str(self._inp, mode)
        return [s for s in self._actions.keys() if re.match(r_str, s)]

    def _fltr_options_shorts(self, mode):
        r_str = self._r_str(self._inp, mode)
        return [s for s in self._options.keys() if re.match(r_str, s)]

    def _fltr_shorts(self, mode='all'):
        act_n = self._fltr_all_actions_short(mode)
        opt_n = self._fltr_options_shorts(mode)
        return act_n + opt_n
