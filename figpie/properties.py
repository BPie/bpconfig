#encoding=utf-8

import inspect
import re
from collections import OrderedDict, Iterable
from copy import copy, deepcopy


class WrongNameException(Exception):
    pass

class NotExecutableException(Exception):
    pass

class NotWriteableException(Exception):
    pass

class NotReadableException(Exception):
    pass

class WrongTypeException(Exception):
    pass

class WrongValueException(Exception):
    pass


class Cell(object):

    TYPE = 'cell'

    def __init__(self, name):
        if not isinstance(name, basestring):
            raise WrongNameException("Wrong argument type (name: string)")
        if not name:
            raise WrongNameException("Wrong argument value (name: not empty)")
        self._name = name

    @property
    def readable(self):
        return false

    @property
    def writeable(self):
        return false

    @property
    def executable(self):
        return hasattr(self, '__call__')

    @property
    def type(self):
        return self.TYPE

    @property
    def name(self):
        return self._name

    def __str__(self):
        return "<Cell({})>".format(self.name)

    @property
    def __call__(self):
        if not self.executable:
            raise NotExecutableException('{}({}) is not executable!'
                    .format(self.TYPE, self.name))



class Action(Cell):

    TYPE = 'action'

    def __init__(self, name, action_f, is_active_f=None):
        Cell.__init__(self, name)
        if not callable(action_f):
            raise WrongTypeException('Given action_f is not callable!')
        # todo: check that the action_f has no arguments
        self._action_f = action_f

        # function that checks if action_f is active
        if is_active_f is None:
            is_active_f = lambda: True
        if not callable(is_active_f):
            raise WrongTypeException('Given is_active_f is not callable!')
        self._is_active_f = is_active_f

    def __str__(self):
        return "<Action({}): {}>".format(self.name, self._action_f)

    def __nonzero__(self):
        return self._is_active_f()

    @property
    def readable(self):
        return False

    @property
    def writeable(self):
        return False

    def __call__(self):
        if self:
            return self._action_f()


class CellContainer(Cell):

    CONTAINED_TYPE = Cell
    EXACT_TYPE = False
    TYPE = 'container'

    ''' Patrern used for auto generating cells '''
    PATTERN = re.compile('_create_(\w+)_prop$', re.IGNORECASE)

    def __init__(self, name, cells=None):
        Cell.__init__(self, name)

        self._cells = []
        if cells is None:
            cells = self._create_cells()

        elif not isinstance(cells, Iterable):
            cells = [cells]

        # separate append so as to check correctness of cells
        for cell in cells:
            self.append(cell)

    ''' Returns  list of (part_name, full_name) function names that matches
    PATTERN.
    '''
    def _get_creators(self):
        methods = [name
                for (name, method)
                in inspect.getmembers(self.__class__, predicate=inspect.ismethod)]

        matches = [self.PATTERN.match(method) for method in methods]
        return [(match.group(), match.group(1)) for match in matches if match]

    ''' Generates cells from methods in the class. '''
    def _create_cells(self):
        return [ Cell.__getattribute__(self, creator_name)()
                for creator_name, _ in self._get_creators() ]

    ''' Helper method if needed for dervative classes '''
    def _append_from_creators(self):
        # separate append so as to check correctness of cells
        for cell in self._create_cells():
            self.append(cell)


    def __str__(self):
        return "<CellContainer[{}]({})>".format(len(self), self.name)

    def __len__(self):
        return len(self._cells)

    def __getitem__(self, name):
        if name.startswith('*'):
            name = name.replace('*','',1)
            private_access = True
        else:
            private_access = False

        allCells = Cell.__getattribute__(self, '_cells')
        cell = next((c for c in allCells if c.name==name), None)

        if isinstance(cell, Property) and not private_access:
            return cell.value
        elif isinstance(cell, Cell):
            return cell
        raise KeyError('name {} not found'.format(name))

    def __setitem__(self, name, value):
        if name.startswith('*'):
            name = name.replace('*','',1)
            private_access = True
        else:
            private_access = False

        allCells = Cell.__getattribute__(self, '_cells')
        cell = next((c for c in allCells if c.name==name), None)

        if private_access:
            raise NotImplementedError('cannot change instance for key')
        elif isinstance(cell, Cell):
            cell.value = value
        elif cell:
            raise KeyError('prop with name {} is not a Cell'.format(name))
        else:
            raise KeyError('prop with name {} not found'.format(name))

        # self.__getattr__(name).value = value

    # def __getitem__(self, name):
    #     for cell in Cell.__getattribute__(self, '_cells'):
    #         if cell.name == name:
    #             return cell
    #     raise KeyError('name {} not found'.format(name))

    def __getattribute__(self, name):
        try:
            return Cell.__getattribute__(self, name)
        except AttributeError:
            return self.__getitem__(name)

        # try:
        #     return Cell.__getattribute__(self, attr)
        # except AttributeError as e:
        #     print 'NO attr named ', attr, e
        #     return self.__getitem__(attr)
        # else:
        #     print 'found attr named ', attr

    def __setattr__(self, name, value):
        if name in self.__dict__:
            # print 'invoked 1 on {}, {}'.format(name,value)
            Cell.__setattr__(self, name, value)
        elif hasattr(self, '_cells') and name in self.keys():
            # print 'invoked 2 on {}, {}'.format(name,value)
            self.__setitem__(name, value)
        else:
            # print 'invoked 3 on {}, {}'.format(name,value)
            Cell.__setattr__(self, name, value)

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
            raise WrongTypeException('cell should be of type {} ({} given)'
                    .format(self.CONTAINED_TYPE, type(cell)))
        elif self.contains(cell.name):
            raise WrongNameException('cell with name {} already exists!'
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

    def __init__(self, name, value, r=True, w=True):
        Cell.__init__(self, name)
        self._r = r
        self._w = True
        self.value = value
        self._w = w

    @property
    def writeable(self):
        return self._w

    @property
    def readable(self):
        return self._r

    @property
    def value(self):
        if not self.readable:
            raise NotReadableException('{}({}) is not readable!'
                    .format(self.TYPE, self.name))

        # if callable(self._value):
        #     return self._value()

        return self._value

    @value.setter
    def value(self, value):
        if not self.writeable:
            raise NotWriteableException('{}({}) is not writeable!'
                    .format(self.TYPE, self.name))

        # if value is None:
        #     raise WrongValueException('Wrong value: cannot be None!')

        if self._additional_value_check(value):
            self._value = value
        else:
            raise WrongValueException('Additional value requirements not met!')

    def _additional_value_check(self, value):
        return True

    def __str__(self):
        return "<{}({}): {}>".format(self.TYPE, self.name, self.value)


class Lambda(Property):

    def __init__(self, name, func, **kwargs):
        if not callable(func):
            raise WrongTypeException('given func <{}> is not callable!'.format(func))

        Property.__init__(self, name, func, **kwargs)
        self._w = False

    @property
    def executable(self):
        return False


    @Property.value.getter
    def value(self):

        if not self.readable:
            raise NotReadableException('{}({}) is not readable!'
                    .format(self.TYPE, self.name))

        return self._value()


class PropertyInt(Property):

    TYPE = 'int'
    _TYPE = int
    _ACCEPTED_TYPES = (basestring,)

    def _convert(self, value):
        if isinstance(value, self._TYPE):
            return value
        elif isinstance(value, self._ACCEPTED_TYPES):
            try:
                return self._TYPE(value)
            except ValueError as e:
                raise WrongValueException('type <{}> matches but could not'
                        'convert value <{}> to type <{}>'
                        .format(type(value), value, self._TYPE))
        else:
            raise WrongTypeException('wrong value type {}, not a TYPE: {}'
                             'nor accepted type {}!'.format(
                                 type(value),
                                 self._TYPE,
                                 self._ACCEPTED_TYPES))

    @Property.value.setter
    def value(self, value):
        if not self.writeable:
            raise NotWriteableException('is not writeable!'
                    .format(self.TYPE, self.name))

        # proper value type
        value = self._convert(value)

        # additional check and final set
        if self._additional_value_check(value):
            self._value = value
        else:
            raise WrongValueException('additional value requirements not met!')


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

    def __init__(self, name, options, value, **kwargs):

        if not options:
            raise WrongValueException('options cannot be empty!')

        if not isinstance(value, basestring):
            raise WrongTypeException('value should be a string type!')

        self._options = StrictCellContainer(name+'\'s container_', options)

        if not self._options.contains(value):
            raise WrongValueException('value {} not found in options {}'
                    .format(value, options))

        PropertyString.__init__(self, name, value, **kwargs)


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


class PropertyBool(PropertyEnum):

    TYPE = 'bool'
    _ACCEPTED_TYPES = (bool, basestring)

    def __init__(self, name, value, **kwargs):
        bool_options = [Cell('True'), Cell('False')]

        if value is True:
            value = 'True'
        elif value is False:
            value = 'False'

        PropertyEnum.__init__(self, name, bool_options, value, **kwargs)

    def __nonzero__(self):
        return self.value == 'True'


class Union(CellContainer):

    TYPE = 'union'

    ''' Patrern used for auto generating map of types -> properties '''
    PATTERN = re.compile('_create_(\w+)_props$', re.IGNORECASE)

    def __init__(self, name, types_map=None):
        Cell.__init__(self, name)

        if types_map == None:
            types_map = self._create_map()

        types = [Cell(s) for s in types_map.keys()]
        self._type = PropertyEnum('type', types, types_map.keys()[0])
        self._map = types_map


    ''' Generates map of types -> properties from methods in the class. '''
    def _create_map(self):
        return { type_name: Cell.__getattribute__(self, creator_name)()
                for creator_name, type_name  in self._get_creators() }


    @property
    def type(self):
        return self._type.value

    # @type.setter
    # def type(self, value):


    @property
    def _cells(self):
        cells = self._map[self.type]
        if isinstance(cells, Cell):
            cells = [cells]
            self._map[self.type] = cells

        cells_copy = copy(cells)

        if not cells_copy:
            cells_copy = []
        elif not isinstance(cells_copy, list):
            cells_copy = [cells_copy]

        cells_copy.append(self._type)
        return cells_copy

    def __str__(self):
        return "<Union[{}]({}: {})>".format(
                len(self),
                self.name,
                self._type.name)

    # def __len__(self):
    #     return len(self._cells)

    # def __getitem__(self, name):
    #     for cell in self._cells:
    #         if cell.name == name:
    #             return cell
    #     else:
    #         raise KeyError('name {} not found'.format(name))

    # def __getattr__(self, attr):
    #     return self.__getitem__(attr)

    # def __setitem__(self, key, value):
    #     self.__getattr__(key).value = value

    # def keys(self):
    #     return [cell.name for cell in self._cells]

    # def values(self):
    #     return copy(self._cells)

    # def contains(self, name):
    #     return name in self.keys()

    # def _is_proper_type(self, cell):
    #     if self.EXACT_TYPE:
    #         return type(cell) is self.CONTAINED_TYPE
    #     else:
    #         return isinstance(cell, self.CONTAINED_TYPE)

    def append(self, cell):
        if not self._is_proper_type(cell):
            raise WrongTypeException('cell should be of type {} ({} given)'
                    .format(self.CONTAINED_TYPE, type(cell)))
        elif self.contains(cell.name):
            raise WrongNameException('cell with name {} already exists!'
                    .format(cell.name))
        else:
            self._map[self._type].append(cell)
            # self._cells.append(cell)

    # def __iter__(self):
    #     for cell in self._cells:
    #         yield cell


if __name__ == '__main__':
    cell = Cell('name')
    print cell.name

