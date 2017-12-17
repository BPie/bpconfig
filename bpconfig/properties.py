# encoding=utf-8
from collections import OrderedDict
from copy import copy, deepcopy


class Cell(object):

    TYPE = 'cell'

    def __init__(self, name):
        if not isinstance(name, basestring):
            raise ValueError("Wrong argument type (name: string)")
        if not name:
            raise ValueError("Wrong argument value (name: not empty)")
        self._name = name

    @property
    def type(self):
        return self.TYPE

    @property
    def name(self):
        return self._name

    def __str__(self):
        return "Cell({})".format(self.name)


class Action(Cell):

    TYPE = 'action'

    def __init__(self, name, action_f, is_active_f=None):
        Cell.__init__(self, name)
        if not callable(action_f):
            raise ValueError('Given action_f is not callable!')
        # todo: check that the action_f has no arguments
        self._action_f = action_f

        # function that checks if action_f is active
        if is_active_f is None:
            is_active_f = lambda: True
        if not callable(is_active_f):
            raise ValueError('Given is_active_f is not callable!')
        self._is_active_f = is_active_f

    def __str__(self):
        return "Action({}): {}".format(self.name, self._action_f)

    def __nonzero__(self):
        return self._is_active_f()

    def __call__(self):
        if self:
            return self._action_f()


class CellContainer(Cell):

    CONTAINED_TYPE = Cell
    EXACT_TYPE = False
    TYPE = 'container'

    def __init__(self, name, cells=None):
        Cell.__init__(self, name)

        self._cells = []
        if cells is not None:
            map(self.append, cells)

    def __str__(self):
        return "CellContainer[{}]({})".format(len(self), self.name)

    def __len__(self):
        return len(self._cells)

    def __getitem__(self, name):
        for cell in self._cells:
            if cell.name == name:
                return cell
        else:
            raise KeyError('name {} not found'.format(name))

    def keys(self):
        return [cell.name for cell in self._cells]

    def values(self):
        return copy(self._cells)

    def contains(self, name):
        return name in self.keys()

    def _is_proper_type(self, cell):
        if self.EXACT_TYPE:
            return type(cell) is self.CONTAINED_TYPE
        else:
            return isinstance(cell, self.CONTAINED_TYPE)

    def append(self, cell):
        if not self._is_proper_type(cell):
            raise ValueError('cell should be of type {} ({} given)'
                    .format(self.CONTAINED_TYPE, type(cell)))
        elif self.contains(cell.name):
            raise ValueError('cell with name {} already exists!'
                    .format(cell.name))
        else:
            self._cells.append(cell)

    def __iter__(self):
        for cell in self._cells:
            yield cell

class StrictCellContainer(CellContainer):

    EXACT_TYPE = True
    TYPE = 'strict container'


class Property(Cell):

    TYPE = 'variant'

    def __init__(self, name, value):
        Cell.__init__(self, name)
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if value is None:
            raise ValueError('Wrong value: cannot be None!')
        if self._additional_value_check(value):
            self._value = value
        else:
            raise ValueError('Additional value requirements not met!')

    def _additional_value_check(self, value):
        return True

    def __str__(self):
        return "prop({}): {}".format(self.name, self.value)


class PropertyInt(Property):

    TYPE = 'int'
    _TYPE = int
    _ACCEPTED_TYPES = (basestring)

    @Property.value.setter
    def value(self, value):

        # proper value type
        if isinstance(value, self._TYPE):
            pass
        elif isinstance(value, self._ACCEPTED_TYPES):
            try:
                value = self._TYPE(value)
            except:
                raise ValueError('Wrong value type: cannot cast from {} to {}'
                        .format(type(value), self._TYPE))
        else:
            raise ValueError('Wrong value type')

        # additional check and final set
        if self._additional_value_check(value):
            self._value = value
        else:
            raise ValueError('Additional value requirements not met!')


class PropertyFloat(PropertyInt):

    TYPE = 'float'
    _TYPE = float
    _ACCEPTED_TYPES = (float, int, basestring)


class PropertyString(PropertyInt):

    TYPE = 'str'
    _TYPE = unicode
    _ACCEPTED_TYPES = (basestring,)


class PropertyEnum(PropertyString):
    ''' class that contains options and has currently set value
    that matches some option's name '''

    TYPE = 'enum'

    def __init__(self, name, options, value):
        if not options:
            raise ValueError('options cannot be empty!')

        if not isinstance(value, basestring):
            raise ValueError('value should be a string type!')

        try:
            self._options = StrictCellContainer(name+'\'s container_', options)
        except Exception as e:
            raise ValueError('Wrong name or options for CellContainer: {}'
                    .format(str(e)))

        if not self._options.contains(value):
            raise ValueError('value {} not found in options {}'
                    .format(value, options))

        try:
            PropertyString.__init__(self, name, value)
        except Exception as e:
            raise ValueError('Wrong name or value for PropertyString: {}'
                    .format(str(e)))

    def _additional_value_check(self, value):
        return self._options.contains(value)

    @property
    def options(self):
        return copy(self._options)

    def __len__(self):
        return len(self._options)

    def __getitem__(self, name):
        return self._options[name]

    def keys(self):
        return self._options.keys()

    def values(self):
        return self._options.values()

    def contains(self, name):
        return self._options.contains(name)


if __name__ == '__main__':
    cell = Cell('name')
    print cell.name
