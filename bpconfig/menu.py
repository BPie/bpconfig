#encoding = utf-8
from __future__ import absolute_import
from __future__ import print_function

import sys
import re
from collections import OrderedDict, defaultdict, deque
from operator import getitem
from blessed import Terminal

from . import properties as props


def short_finder(names, mapped_short=None, generator=None, banned=None):
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
        mapped_short = short_finder(names=names, mapped_short=mapped_short,
                generator=generator, banned=banned)

    return mapped_short


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
        self._flags = defaultdict( lambda: False, {
            'type': True,
            'name': True,
            'short': True,
            'value': True})
        self._info = ''
        self._debug = deque([], maxlen=5)
        self._inp = ''
        self._inp_spc = ''
        self._loc_cache = {}

        actions = {}
        actions['h'] = props.Action(
                'left',
                lambda: self._go_down(),
                lambda: not self._in_root)
        actions['j'] = props.Action(
                'down',
                lambda: self._highlight_down(),
                lambda: self._state == 'container')
        actions['k'] = props.Action(
                'up',
                lambda: self._highlight_up(),
                lambda: self._state == 'container')
        actions['l'] = props.Action(
                'right',
                lambda: self._go_up(self._highlighted),
                lambda: (self._state in ('container', 'enum')
                        and self._highlighted))
        cancel_action = props.Action(
                'cancel',
                lambda: self._cancel,
                lambda: self._state in ('container', 'enum'))
        actions['KEY_ESCAPE'] = cancel_action
        actions['cancel'] = cancel_action

        accept_action = props.Action(
                'accept',
                lambda: self._cancel,
                lambda: self._state in ('container', 'enum'))
        actions['KEY_ENTER'] = accept_action
        actions['accept'] = accept_action

        actions['Q'] = props.Action('quit', lambda: sys.exit())
        self._actions = actions

    @property
    def _highlighted(self):
        return None

    def _highlight_down(self):
        pass

    def _highlight_up(self):
        pass
    @property
    def _current(self):
        return reduce(getitem, self._pos[1:], self._container)

    @property
    def _state(self):
        if isinstance(self._current, props.PropertyEnum):
            return 'enum'
        elif isinstance(self._current, props.Property):
            return 'property'
        elif isinstance(self._current, props.CellContainer):
            return 'container'

    @property
    def _parent(self):
        return reduce(getitem, self._pos[1:-1], self._container)


    def _print_header(self):
        with self._t.location(0,0):
            tail = self._pos[:-1]
            head = self._pos[-1]
            print(self._t.center(self._t.black_on_white('/'.join(tail))
                    + self._t.bold_black_on_white('/'+head)))


    def _formated_cell_attr(self, cell, attrname, str_template):
        if not self._flags[attrname] or not hasattr(cell, attrname):
            return ''

        attr_val = getattr(cell, attrname)
        filled = str_template.format(attr_val)
        formatted = self._formater(cell, attrname)(filled)
        return formatted

    def _formater(self, cell, attrname='name'):
        if isinstance(cell, props.CellContainer):
            return self._cont_f(cell, attrname)
        elif isinstance(cell, props.PropertyEnum):
            return self._enum_f(cell, attrname)
        elif isinstance(cell, props.Action):
            return self._act_f(cell, attrname)
        elif hasattr(cell, 'value'):
            return self._val_f(cell, attrname)
        else:
            return self._cell_f(cell, attrname)

    @property
    def _empty_formatter(self):
        return self._t.white

    def _cell_f(self, cell, attrname):
        return self._empty_formatter

    def _cont_f(self, cell, attrname):
        if attrname == 'type':
            return self._t.yellow
        else:
            return self._empty_formatter

    def _val_f(self, cell, attrname):
        if attrname == 'type':
            return self._t.blue
        else:
            return self._empty_formatter

    def _enum_f(self, cell, attrname):
        if attrname == 'type':
            return self._t.magenta
        else:
            return self._empty_formatter

    def _act_f(self, cell, attrname):
        if attrname == 'type':
            return self._t.green
        else:
            return self._empty_formatter

    def _mark_name(self, name, short, f=None):
        # default formatter
        if not f:
            f = self._t.cyan

        # need to add info about short if not found in name
        if not re.findall(short, name, flags=re.IGNORECASE):
            name = '[{}]: '.format(short) + name
        return re.sub(short, f(short), name, 1, re.IGNORECASE)
        # return name.lower().replace(short.lower(), f(short), 1)

    def _print_option(self, cell, short, formatter=None):
        msg = ''
        attrstr = lambda n,t: self._formated_cell_attr(cell, n, t)
        name = attrstr('name', '{}')
        marked = self._mark_name(name, short)
        msg += self._t.rjust(attrstr('type', '[{}] '), width=15)
        msg += self._t.center(marked, width=10)
        msg += self._t.ljust(attrstr('value', '= {}'), width=15)

        if formatter is None:
            formatter = self._empty_formatter
        print(formatter(self._t.center(msg)))

    @property
    def _options(self):
        return self._get_options(self._current)

    @property
    def _parent_options(self):
        return self._get_options(self._parent)

    def _get_options(self, container):
        # cells
        cells = container.values()

        # shorts
        shorts_taken = self._actions.keys()
        shorts = short_finder(container.keys(), banned=shorts_taken)

        # combine
        return OrderedDict(zip(shorts, cells))

    def _print_current(self):
        if isinstance(self._current, props.CellContainer):
            self._print_options()
        elif isinstance(self._current, props.Property):
            self._print_edit()
        else:
            pass


    def _print_options(self):
        assert self._state == 'container'
        with self._t.location(0,2):
            print(self._t.center(' ~~~< options >~~~ '))
            for short, cell in self._options.iteritems():
                self._print_option(cell, short)

    def _print_edit(self):
        assert self._state == 'property'
        with self._t.location(0,2):
            print(self._t.center(' ~~~< edit >~~~ '))
            for short, cell in self._parent_options.iteritems():
                if cell == self._current:
                    formatter = None
                else:
                    formatter = self._t.dim
                self._print_option(cell, short, formatter)

    def _go_up(self, name):
        try:
            new_cell = self._current[name]
        except:
            raise RuntimeWarning('wrong child name: {}'.format(name))
        else:
            self._pos.append(new_cell.name)


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

    @property
    def _in_root(self):
        return len(self._pos) == 1

    def _go_down(self):
        if self._in_root:
            raise RuntimeWarning('you\'re in root')
        else:
            self._pos = self._pos[:-1]

    def _clear(self):
        print(self._t.clear())

    @property
    def _current_loc(self):
        return self._t.get_location()

    def _print_debug(self):
        if not self._debug or self._t.height < 20:
            return

        h = self._t.height - 6
        with self._t.location(0, h):
            print('## debug ##', end='')
            for i,d in enumerate(self._debug):
                print(' || #{}: {}'.format(i,d), end='')


    def _print_footer(self):
        th = self._t.height
        prompt = ' >>> {}'.format(self._inp)
        msgs = {
                th: prompt,
                th-1: ' ',
                th-2: '_'*self._t.width,
                th-3: self._info
                }

        for h, msg in msgs.iteritems():
            with self._t.location(0, h):
                print(msg, end='')
                if msg == prompt:
                    x = self._current_loc[1]
                    y = self._current_loc[0]
                    self._loc_cache['prompt'] = x, y


    def _gather_inp(self):
        x, y = self._loc_cache["prompt"][1], self._loc_cache["prompt"][0]
        with self._t.location(*self._loc_cache['prompt']):
            with self._t.cbreak():
                val = self._t.inkey(timeout=1)
                if not val:
                    self._inp_spc = 'timeout'
                elif val.is_sequence and val.name in ('KEY_ENTER', 'KEY_ESCAPE'):
                    self._inp_spc = val.name
                elif len(str(val)) == 1:
                    self._inp += str(val)
                else:
                    self._info = 'unhandled inp character: [{}]'.format(val)

    def _clean_inp(self):
        self._inp = ''
        self._inp_spc = ''


    @property
    def _inp_spc_meaning(self):
        if self._inp_spc in ('KEY_ESCAPE',):
            return 'cleaning'
        elif self._inp_spc in ('KEY_ENTER', 'timeout'):
            return 'consume'
        else:
            return None

    def _handle_inp(self):
        if self._inp_spc_meaning == 'cleaning':
            self._info = 'inp cleaned'
            self._clean_inp()
        elif len(self._fltr_shorts('all')) <= 0:
            self._info = 'wrong inp: [{}]!'.format(self._inp)
            self._clean_inp()
        elif len(self._fltr_shorts('all')) == 1 or \
                 (self._inp_spc_meaning == 'consume' and self._inp):
            self._consume_inp()
            self._clean_inp()
        else:
            add_msg =  r' waiting for inp ...'
            if not re.findall(add_msg, self._info):
                self._info += ' (' + add_msg + ')'

    def _cancel(self):
        pass

    def _timeout(self):
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

    def run(self):
        with self._t.fullscreen():
            while(True):
                self._clear()
                self._print_header()
                self._print_current()
                self._print_debug()
                self._print_footer()
                self._gather_inp()
                self._handle_inp()


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

    # some_list = [
    #         'name',
    #         'nome',
    #         'far',
    #         'foo',
    #         'bar',
    #         'noob',
    #         'something',
    #         'quant']


    # print(fingerprint_finder(some_list))


