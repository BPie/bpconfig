import sys
import unittest
import bpconfig.properties as props
from itertools import product


class TestCell(unittest.TestCase):

    def setUp(self):
        pass

    def test_proper_name(self):
        name = 'name'
        cell = props.Cell('name')
        self.assertEqual(name, cell.name)

    def test_wrong_name(self):
        names = [123, 123.1, ['a','b']]

        for name in names:
            self.assertRaises(ValueError, lambda n: props.Cell(n), name)

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

    def test_constructor_proper(self):
        for proper_cells in self.PROPER_CELLS_LIST:
            try:
                cc = props.CellContainer(self.NAME, proper_cells)
            except:
                self.fail('exception occured for {}!'
                        .format(proper_cells))

    def test_constructor_wrong(self):
        for wrong_cells in self.WRONG_CELLS_LIST:
            try:
                cc = props.CellContainer(self.NAME, proper_cells)
            except:
                pass
            else:
                self.fail('exception not occured for {}'
                        .format(wrong_cells))

    def test_len(self):
        for proper_cells in self.PROPER_CELLS_LIST:
            cc = props.CellContainer(self.NAME, proper_cells)
            self.assertEqual(len(cc), len(proper_cells))

    def test_getitem_and_contains(self):
        ok_cell_names = ['c1', 'c2', '111']
        cells = [props.Cell(name) for name in ok_cell_names]

        ok_prop_names = ['p1']
        ok_prop_starting_vals = [1]
        properties = [props.Property(name, val)
                for name, val
                in zip(ok_prop_names, ok_prop_starting_vals)]

        cc = props.CellContainer(self.NAME, cells+properties)

        # checking added names
        cells_and_props = cells + properties
        for cell in cells_and_props:
            name = cell.name
            self.assertTrue(cc.contains(name))
            self.assertEqual(cc[name], cell)

        # assert this becouse we want to check if self.name is not automatically
        # added to keys (names)
        assert self.NAME not in ok_prop_names
        assert self.NAME not in ok_cell_names

        # checking not added names
        wrong_names = ['other', 111, None, self.NAME]
        for wrong_name in wrong_names:
            self.assertFalse(cc.contains(wrong_name))
            self.assertRaises(KeyError, lambda: cc[wrong_name])

    def test_keys_and_values(self):
        names = ['a', 'z', '111', 'b', 'lorem ipsum']
        cells = [props.Cell(name) for name in names]
        cc = props.CellContainer(self.NAME, cells)
        self.assertEqual(cc.keys(), names)
        self.assertEqual(cc.values(), cells)

        copy_cells = cc.values()
        copy_names = cc.keys()
        copy_cells.append('test')
        copy_names.append('test')

        self.assertEqual(cc.keys(), names)
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

    def test_prop_value_changed_append(self):
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
            except:
                self.fail('Wrong exception while adding prop of name {}'
                        .format(cell.name))
            else:
                self.fail('No exception while adding prop of name {}'
                        .format(cell.name))


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
                self.fail("wrong exception, given {}".format(wrong_value))
            else:
                self.fail("not raised for {}".format(wrong_value))


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


class TestPropertyEnum(unittest.TestCase):

    NAME = 'name'

    def setUp(self):
        pass

    def test_constructor(self):
        good_options_list = [
                [props.Cell('a')],
                [props.Cell('a'), props.Cell('b')] ]
        for good_options in good_options_list:
            value = good_options[0].name
            try:
                enum = props.PropertyEnum(self.NAME, good_options, value)
            except Exception as e:
                self.fail('Exception occured for name: {}, opts: {}, '
                          'val: {}: {}'
                          .format(self.NAME, good_options, value, str(e)))

    def test_constructor_exception(self):
        wrong_options_list = [
                [],
                [None],
                [props.Cell('a'), 1],
                [props.Cell('a'), props.Cell('a')],
                [props.Cell('a'), props.Property('b',1)]]

        for wrong_options in wrong_options_list:
            try:
                value = wrong_options[0].name
            except:
                value = None
            try:
                enum = props.PropertyEnum(self.NAME, wrong_options, value)
            except ValueError:
                pass
            except:
                self.fail('Wrong exception!')
            else:
                self.fail('No exception for name: {}, wrong opts: {}, val: {}'
                        .format(self.NAME, wrong_options, value))

    def test_constructor_wrong_values_exception(self):
        good_options_list = [
                [props.Cell('a')],
                [props.Cell('a'), props.Cell('b')] ]
        wrong_values = ['c', 'd', None, [], props.Cell('a')]

        for options, w_vals in product(good_options_list, wrong_values):
            try:
                enum = props.PropertyEnum(self.NAME, options, w_vals)
            except ValueError:
                pass
            except Exception as e:
                self.fail('Wrong exception!: {}, {}'.format(type(e), str(e)))
            else:
                self.fail('No exception for name: {}, opts: {}, wrong val: {}'
                    .format(self.NAME, options, w_vals))




if __name__ == '__main__':
    unittest.main()
