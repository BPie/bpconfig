# encoding=utf-8
from collections import OrderedDict
from copy import copy


class Cell(object):

    def __init__(self, name):
        if not isinstance(name, basestring):
            raise ValueError("Wrong argument type (name: string)")
        if not name:
            raise ValueError("Wrong argument value (name: not empty)")
        self._name = name

    @property
    def name(self):
        return self._name

    def __str__(self):
        return "Cell({})".format(self.name)


class CellContainer(Cell):
    CONTAINED_TYPE = Cell

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


class Property(Cell):

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
        self._value = value


class PropertyInt(Property):

    _TYPE = int
    _ACCEPTED_TYPES = (basestring)

    @Property.value.setter
    def value(self, value):
        if isinstance(value, self._TYPE):
            self._value = value
        elif isinstance(value, self._ACCEPTED_TYPES):
            try:
                value = self._TYPE(value)
            except:
                raise ValueError('Wrong value type: cannot cast from {} to {}'
                        .format(type(value), self._TYPE))
            else:
                self._value = value
        else:
            raise ValueError('Wrong value type')


class PropertyFloat(PropertyInt):

    _TYPE = float
    _ACCEPTED_TYPES = (float, int, basestring)


class PropertyString(PropertyInt):

    _TYPE = unicode
    _ACCEPTED_TYPES = (basestring,)


class PropertyEnum(CellContainer, PropertyString):
    ''' class that contains options and has currently set value
    that matches some option's name '''

    def __init__(self, name, options, value):
        if not options:
            raise ValueError('options cannot be empty!')

        if not isinstance(value, basestring):
            raise ValueError('value should be a string type!')

        try:
            CellContainer.__init__(self, name, options)
        except Exception as e:
            raise ValueError('Wrong name or options for CellContainer: {}'
                    .format(str(e)))


        if not self.contains(value):
            raise ValueError('value {} not found in options {}'
                    .format(value, options))

        try:
            PropertyString.__init__(self, name, value)
        except Exception as e:
            raise ValueError('Wrong name or value for PropertyString: {}'
                    .format(str(e)))


    def _is_proper_type(self, option):
        ''' accepts only pure Cells types'''
        return type(option) is Cell

    # @PropertyString.value.setter
    # def value(self):
    #     pass

if __name__ == '__main__':
    cell = Cell('name')
    print cell.name
