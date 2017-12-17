#encoding = utf-8
from __future__ import absolute_import
from __future__ import print_function

from blessed import Terminal

from . import properties as props


class StyleFactory(object):

    def __init__(self, terminal):
        self._t = terminal


    def __call__(self, cell=None, attrname='name'):
        if cell is None:
            return self._default_style
        elif isinstance(cell, props.CellContainer):
            return self._cont_style(cell, attrname)
        elif isinstance(cell, props.PropertyEnum):
            return self._enum_style(cell, attrname)
        elif isinstance(cell, props.Action):
            return self._act_style(cell, attrname)
        elif hasattr(cell, 'value'):
            return self._val_style(cell, attrname)
        else:
            return self._cell_style(cell, attrname)

    @property
    def _default_style(self):
        return self._t.white

    def _cell_style(self, cell, attrname):
        return self._default_style

    def _cont_style(self, cell, attrname):
        if attrname == 'type':
            return self._t.yellow
        else:
            return self._default_style

    def _val_style(self, cell, attrname):
        if attrname == 'type':
            return self._t.blue
        else:
            return self._default_style

    def _enum_style(self, cell, attrname):
        if attrname == 'type':
            return self._t.magenta
        else:
            return self._default_style

    def _act_style(self, cell, attrname):
        if attrname == 'type':
            return self._t.green
        else:
            return self._default_style
