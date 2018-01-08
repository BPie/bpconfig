#encoding=utf-8

import sys
import unittest
import bpconfig.properties as props
from itertools import product
from ddt import ddt, data, file_data, unpack


@ddt
class TestCell(unittest.TestCase):

    def setUp(self):
        pass

    def test_proper_name(self):
        name = 'name'
        cell = props.Cell('name')
        self.assertEqual(name, cell.name)

    @data(123, 123.1, ['a','b'])
    def test_wrong_name(self, name):
        self.assertRaises(ValueError, lambda n: props.Cell(n), name)


@ddt
class TestAction(unittest.TestCase):

    def setUp(self):
        pass

    @data(1, 's', None, lambda x: x+1)
    def test_action_as_function(self, ret_val):
        def foo():
            return ret_val

        a = props.Action('name', foo)
        self.assertEqual(a(), ret_val)

    def test_action_as_lambda(self):
        a = props.Action('name', lambda: 1)
        self.assertEqual(a(), 1)

    @data(1, None, 's')
    def test_action_exception(self, n_call):
        assert(not callable(n_call))
        self.assertRaises(ValueError, lambda: props.Action('name', n_call))

    def test_is_callable(self):
        a = props.Action('name', lambda: 1)
        self.assertTrue(callable(a))

    @unittest.skip('not implemented')
    def test_function_with_args(self):
        pass


@ddt
class TestCellContainer(unittest.TestCase):

    NAME = 'name'
    DEFAULT_CELLS = None
    PROPER_CELLS_LIST = [
            [],
            [props.Cell('a'), props.Cell('b')],
            [props.Property('plain', 1),
                props.PropertyFloat('float', 1.3),
                props.PropertyInt('int', 1),
                props.PropertyString('string', 'v'),
                props.CellContainer('container')]]

    WRONG_CELLS_LIST = [
            [1],
            ['abc'],
            [props.Cell('a'), props.Cell('a')],
            [props.Cell('a'), props.CellContainer('a')],
            [props.Cell('a'), 1]]


    def setUp(self):
        pass

    @data(*PROPER_CELLS_LIST)
    def test_constructor_proper(self, proper_cells):
        try:
            cc = props.CellContainer(self.NAME, proper_cells)
        except:
            self.fail('exception occured for {}!'
                    .format(proper_cells))

    @data(*WRONG_CELLS_LIST)
    def test_constructor_wrong(self, wrong_cells):
        try:
            cc = props.CellContainer(self.NAME, proper_cells)
        except:
            pass
        else:
            self.fail('exception not occured for {}'
                    .format(wrong_cells))

    @data(*PROPER_CELLS_LIST)
    def test_len(self, proper_cells):
        cc = props.CellContainer(self.NAME, proper_cells)
        self.assertEqual(len(cc), len(proper_cells))

    @unpack
    @data(
        { 'key': 'k', 'names': ['a', 'b', 'c', 'k']},
        { 'key': 'a', 'names': ['a']}
    )
    def test_getitem(self, key, names):
        cells = [props.Cell(name) for name in names]
        cc = props.CellContainer(self.NAME, cells)
        self.assertEqual(cc[key].name, key)

    @unpack
    @data(
        { 'key': 'k', 'names': ['a', 'b', 'c', 'k']},
        { 'key': 'a', 'names': ['a']}
    )
    def test_contains(self, key, names):
        cells = [props.Cell(name) for name in names]
        cc = props.CellContainer(self.NAME, cells)
        self.assertTrue(cc.contains(key))

    @unpack
    @data(
        { 'key': 'z', 'names': ['a', 'b', 'c', 'k']},
        { 'key': 'A', 'names': ['a']}
    )
    def test_getitem_assert(self, key, names):
        cells = [props.Cell(name) for name in names]
        cc = props.CellContainer(self.NAME, cells)
        self.assertRaises(KeyError, lambda: cc[key])

    @unpack
    @data(
        { 'key': 'z', 'names': ['a', 'b', 'c', 'k']},
        { 'key': 'A', 'names': ['a']}
    )
    def test_not_contains(self, key, names):
        cells = [props.Cell(name) for name in names]
        cc = props.CellContainer(self.NAME, cells)
        self.assertFalse(cc.contains(key))

    def test_getitem_same(self):
        cells = [props.Cell('cell'), props.Property('prop', 1)]
        cc = props.CellContainer(self.NAME, cells)
        for cell in cells:
            key = cell.name
            self.assertEqual(cell, cc[key])

    def test_not_contains_own_name(self):
        names = ['a', 'b', 'c', 'd']
        cells = [ props.Cell(name) for name in names ]
        cc = props.CellContainer('name', cells)
        self.assertFalse(cc.contains('name'))

    def test_keys(self):
        names = ['a', 'z', '111', 'b', 'lorem ipsum']
        cells = [props.Cell(name) for name in names]
        cc = props.CellContainer(self.NAME, cells)
        self.assertEqual(cc.keys(), names)

    def test_values(self):
        names = ['a', 'z', '111', 'b', 'lorem ipsum']
        cells = [props.Cell(name) for name in names]
        cc = props.CellContainer(self.NAME, cells)
        self.assertEqual(cc.values(), cells)

    def test_prop_value(self):
        p1 = props.Property('p1', 1)
        p2 = props.Property('p2', 2)
        cells = [p1, p2]
        cc = props.CellContainer(self.NAME, cells)
        self.assertEqual(cc['p1'].value, 1)
        self.assertEqual(cc['p2'].value, 2)

    def test_prop_value_append(self):
        cc = props.CellContainer(self.NAME, [])

        p = props.Property('p', 1)
        cc.append(p)
        self.assertEqual(cc['p'].value, 1)

    def test_prop_value_changed(self):
        p1 = props.Property('p1', 1)
        p2 = props.Property('p2', 2)
        cells = [p1, p2]
        cc = props.CellContainer(self.NAME, cells)
        p2.value = 22
        self.assertEqual(cc['p1'].value, 1)
        self.assertEqual(cc['p2'].value, 22)

        cc['p1'].value = 11
        self.assertEqual(p1.value, 11)
        self.assertEqual(p2.value, 22)

    def test_prop_appended_value_changed(self):
        cc = props.CellContainer(self.NAME, [])

        p = props.Property('p', 1)
        cc.append(p)
        self.assertEqual(cc['p'].value, 1)

        p.value = 11
        self.assertEqual(cc['p'].value, 11)

        cc['p'].value = 111
        self.assertEqual(p.value, 111)

    def test_append(self):
        sc_names = ['1', '2']
        starting_cells = [props.Cell(name) for name in sc_names]

        ac_names = ['3', '4', self.NAME]
        cells_to_append = [props.Cell(name) for name in ac_names]

        cc = props.CellContainer(self.NAME, starting_cells)
        for cell in cells_to_append:
            cc.append(cell)

        for name in sc_names+ac_names:
            self.assertTrue(cc.contains(name))

    def test_append_fails(self):
        sc_names = ['1', '2']
        starting_cells = [props.Cell(name) for name in sc_names]

        from copy import deepcopy
        ac_names = deepcopy(sc_names)
        cells_to_append = [props.Cell(name) for name in ac_names]

        cc = props.CellContainer(self.NAME, starting_cells)
        for cell in cells_to_append:
            try:
                cc.append(cell)
            except ValueError:
                pass
            except Exception as e:
                self.fail('Wrong exception!: {}, {}'.format(type(e), str(e)))
            else:
                self.fail('No exception while adding prop of name {}'
                        .format(cell.name))

@ddt
class TestStrictCellContainer(unittest.TestCase):

    @data(
        [],
        [props.Cell('a')],
        [props.Cell('a'), props.Cell('b')]
    )
    def test_constructor(self, cells):
        try:
            scc = props.StrictCellContainer('n', cells)
        except Exception as e:
            self.fail('Exception: {}'.format(str(e)))

    @data(
        [props.Cell('a'), props.Cell('a')],
        [props.Cell('a'), props.Property('b', 1)],
        [props.Property('a', 1)],
        [props.PropertyInt('a', 2)]
    )
    def test_constructor_exception(self, cells):
        try:
            scc = props.StrictCellContainer('n', cells)
        except ValueError:
            pass
        except Exception as e:
            self.fail('Wrong Exception: {}!'.format(str(e)))
        else:
            self.fail('Exception not occured for {}!'.format(cells))

    @data(props.Cell('a'))
    def test_append(self, cell):
        scc = props.StrictCellContainer('n', [props.Cell('x')])
        try:
            scc.append(cell)
        except Exception as e:
            self.fail('Exception: {}'.format(str(e)))

    @data(
        props.Cell('x'),
        props.Property('b', 1),
        props.PropertyInt('a', 2)
    )
    def test_append_exception(self, cell):
        scc = props.StrictCellContainer('n', [props.Cell('x')])
        try:
            scc.append(cell)
        except ValueError:
            pass
        except Exception as e:
            self.fail('Wrong Exception: {}!'.format(str(e)))
        else:
            self.fail('Exception not occured for {}!'.format(cell))

@ddt
class TestProperty(unittest.TestCase):

    name = 'name'
    DEFAULT_VALUE = 0
    PROPER_VALUES = [1, 1., 'value', props.Cell('name')]
    WRONG_VALUES = [None]
    TYPE = props.Property

    def test_constructor(self):
        for proper_value in self.PROPER_VALUES:
            try:
                cell = self.TYPE(self.name, proper_value)
            except:
                e = sys.exc_info()[0]
                self.fail('constructor failed for name {} and value {} ({})'
                          .format(self.name, proper_value, str(e)))

    def test_equal_constructor(self):
        for proper_value in self.PROPER_VALUES:
            cell = self.TYPE(self.name, proper_value)
            self.assertEqual(proper_value, cell.value)

    def test_equal_asign(self):
        cell = self.TYPE(self.name, self.DEFAULT_VALUE)
        for proper_value in self.PROPER_VALUES:
            cell.value = proper_value
            self.assertEqual(proper_value, cell.value)

    def test_wrong_value(self):
        prop = self.TYPE(self.name, self.DEFAULT_VALUE)
        for wrong_value in self.WRONG_VALUES:
            try:
                cell = self.TYPE(self.name, wrong_value)
            except ValueError:
                pass
            else:
                self.fail('no value raise for value = {}!'
                        .format(wrong_value))

    def test_equal_asign_except(self):
        cell = self.TYPE(self.name, self.DEFAULT_VALUE)
        for wrong_value in self.WRONG_VALUES:
            try:
                cell.value = wrong_value
            except ValueError:
                pass
            except:
                self.fail('wrong exception, given {}'.format(wrong_value))
            else:
                self.fail('not raised for {}'.format(wrong_value))


class TestPropertyInt(TestProperty):

    PROPER_VALUES = [-1, 0, 1,1000, '1']
    WRONG_VALUES = [-1.1, 0.1, 1.1, 'str']
    DEFAULT_VALUE = 0
    TYPE = props.PropertyInt

    def test_equal_constructor(self):
        for proper_value in self.PROPER_VALUES:
            cell = self.TYPE(self.name, proper_value)
            casted_value = self.TYPE._TYPE(proper_value)
            self.assertEqual(casted_value, cell.value)

    def test_equal_asign(self):
        cell = self.TYPE(self.name, self.DEFAULT_VALUE)
        for proper_value in self.PROPER_VALUES:
            cell.value = proper_value
            casted_value = self.TYPE._TYPE(proper_value)
            self.assertEqual(casted_value, cell.value)

    def test_proper_value_type_constructor(self):
        for proper_value in self.PROPER_VALUES:
            some_prop = self.TYPE(self.name, proper_value)
            self.assertTrue(isinstance(some_prop.value, self.TYPE._TYPE))

    def test_proper_value_type_asign(self):
        cell = self.TYPE(self.name, self.DEFAULT_VALUE)
        for proper_value in self.PROPER_VALUES:
            self.assertTrue(isinstance(cell.value, self.TYPE._TYPE))


class TestPropertyFloat(TestPropertyInt):

    PROPER_VALUES = [-1., 0., 1.1,100., 1000.2, '2', '-4', '3.5', '-1.4']
    WRONG_VALUES = ['str', [-2], (-3,2)]
    DEFAULT_VALUE = 0.
    TYPE = props.PropertyFloat

class TestPropertyString(TestPropertyInt):

    PROPER_VALUES = ['sting', 'long string \nlorem ipsum', u'unicode string',
            u'śćźżóęą']
    WRONG_VALUES = [(1,3), [1,2,3.4]]
    DEFAULT_VALUE = 's'
    TYPE = props.PropertyString


@ddt
class TestPropertyEnum(unittest.TestCase):

    NAME = 'name'

    def setUp(self):
        self.good_vals = ['a', 'b', 'c']
        self.init_val = self.good_vals[0]
        self.bad_vals = ['A', self.NAME, None, 0]
        options = [props.Cell(v) for v in self.good_vals]

        self.enum = props.PropertyEnum(self.NAME, options, self.init_val)


    @data(
        [props.Cell('a')],
        [props.Cell('a'), props.Cell('b')]
    )
    def test_constructor(self, good_options):
        value = good_options[0].name
        try:
            enum = props.PropertyEnum(self.NAME, good_options, value)
        except Exception as e:
            self.fail('Exception occured for name: {}, opts: {}, '
                      'val: {}: {}'
                      .format(self.NAME, good_options, value, str(e)))

    @data(
        [],
        [None],
        [props.Cell('a'), 1],
        [props.Cell('a'), props.Cell('a')],
        [props.Cell('a'), props.Property('b',1)]
    )
    def test_constructor_exception(self, wrong_options):
        try:
            value = wrong_options[0].name
        except:
            value = None
        try:
            enum = props.PropertyEnum(self.NAME, wrong_options, value)
        except ValueError:
            pass
        except Exception as e:
            self.fail('Wrong exception!: {}, {}'.format(type(e), str(e)))
        else:
            self.fail('No exception for name: {}, wrong opts: {}, val: {}'
                    .format(self.NAME, wrong_options, value))

    @data('c', 'd', None, [], props.Cell('a'))
    def test_constructor_wrong_values_exception(self, wrong_val):
        options = [props.Cell('a'), props.Cell('b')]

        try:
            enum = props.PropertyEnum(self.NAME, options, wrong_val)
        except ValueError:
            pass
        except Exception as e:
            self.fail('Wrong exception!: {}, {}'.format(type(e), str(e)))
        else:
            self.fail('No exception for name: {}, opts: {}, wrong val: {}'
                .format(self.NAME, options, wrong_val))

    def test_not_as_container(self):
        pass

    def test_value(self):
        self.assertEqual(self.enum.value, self.init_val)

    def test_set_value(self):
        for v in self.good_vals:
            self.enum.value = v
            self.assertEqual(self.enum.value, v)

    def test_set_value_exception(self):
        for v in self.bad_vals:
            try:
                self.enum.value = v
            except ValueError:
                pass
            except Exception as e:
                self.fail('Wrong exception!: {}, {}'.format(type(e), str(e)))
            else:
                self.fail('No exception for wrong val: {}'.format(v))

    def test_options(self):
        options = self.enum.options

        for val in self.good_vals:
            self.assertTrue(options.contains(val))

    @unittest.skip("not implemented")
    def test_loop_options(self):
        try:
            for opt in self.enum.options:
                self.assertNotNull(opt)
        except Exception as e:
            self.fail('failed to loop, exception raisd: {}'.format(str(e)))

@ddt
class TestPropertyUnion(unittest.TestCase):

    NAME = 'name'

    @data(
        {
            'a': [props.Cell('a1'), props.Cell('a2')],
            'b': [props.Cell('b1')]
        }
    )
    def test_constructor(self, type_map):
        try:
            union = props.Union(self.NAME, type_map)
        except Exception as e:
            self.fail('Exception occured for name: {}, type_map: {}, '
                      ': {}'
                      .format(self.NAME, type_maplue, str(e)))

    @data(
        {
            'a': [props.Cell('a1'), props.Cell('a2')],
            'b': [props.Cell('b1')]
        }
    )
    def test_change_type(self, type_map):
        union = props.Union(self.NAME, type_map)

        try:
            for possible_type in type_map.keys():
                union['type'].value = possible_type
        except KeyError() as e:
            self.fail('Exception occured for type {} : {}'
                    .format(possible_type, e))


    @unpack
    @data(
        (
            {
                'a': [props.Cell('a1'), props.Cell('a2')],
                'b': [props.Cell('b1')]
            },
            ['c', 'A', 'aa']
        )
    )
    def test_change_type(self, type_map, bad_types):
        union = props.Union(self.NAME, type_map)

        for bad_type in bad_types:
            try:
                union['type'].value = bad_type
            except ValueError as e:
                pass
            else:
                self.fail('Exception NOT occured for type {} : {}'
                        .format(possible_type, e))



if __name__ == '__main__':
    unittest.main()
