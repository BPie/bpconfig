#encoding=utf-8

import sys
import unittest
import figpie as fp
from itertools import product
from ddt import ddt, data, file_data, unpack


@ddt
class TestCell(unittest.TestCase):

    TYPE_NAME='cell'
    def test_proper_name(self):
        name = 'name'
        cell = fp.Cell('name')
        self.assertEqual(name, cell.name)

    @data(123, 123.1, ['a','b'])
    def test_wrong_name(self, name):
        self.assertRaises(ValueError, lambda n: fp.Cell(n), name)

    def test_type(self):
        cell = fp.Cell('name')
        self.assertEqual(cell.type, self.TYPE_NAME)
        self.assertEqual(cell.TYPE, self.TYPE_NAME)



@ddt
class TestAction(unittest.TestCase):

    TYPE_NAME = 'action'
    @data(1, 's', None, lambda x: x+1)
    def test_action_as_function(self, ret_val):
        def foo():
            return ret_val

        a = fp.Action('name', foo)
        self.assertEqual(a(), ret_val)

    def test_action_as_lambda(self):
        a = fp.Action('name', lambda: 1)
        self.assertEqual(a(), 1)


    @data(1, None, 's')
    def test_action_exception(self, n_call):
        assert(not callable(n_call))
        self.assertRaises(RuntimeError, lambda: fp.Action('name', n_call))

    def test_is_callable(self):
        a = fp.Action('name', lambda: 1)
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
            [fp.Cell('a'), fp.Cell('b')],
            [fp.Property('plain', 1),
                fp.PropertyFloat('float', 1.3),
                fp.PropertyInt('int', 1),
                fp.PropertyString('string', 'v'),
                fp.CellContainer('container')]]

    WRONG_CELLS_LIST = [
            [1],
            ['abc'],
            [fp.Cell('a'), fp.Cell('a')],
            [fp.Cell('a'), fp.CellContainer('a')],
            [fp.Cell('a'), 1]]

    TYPE_NAME = 'container'

    def test_constructor_proper(self):
        for proper_cells in self.PROPER_CELLS_LIST:
            try:
                cc = fp.CellContainer(self.NAME, proper_cells)
            except:
                self.fail('exception occured for {}!'
                        .format(proper_cells))

    def test_constructor_wrong(self):
        for wrong_cells in self.WRONG_CELLS_LIST:
            try:
                cc = fp.CellContainer(self.NAME, wrong_cells)
            except:
                pass
            else:
                self.fail('exception not occured for {}'
                        .format(wrong_cells))

    def test_len(self):
        for proper_cells in self.PROPER_CELLS_LIST:
            cc = fp.CellContainer(self.NAME, proper_cells)
            self.assertEqual(len(cc), len(proper_cells))

    @unpack
    @data(
        { 'key': 'k', 'names': ['a', 'b', 'c', 'k']},
        { 'key': 'a', 'names': ['a']}
    )
    def test_getitem(self, key, names):
        cells = [fp.Cell(name) for name in names]
        cc = fp.CellContainer(self.NAME, cells)
        self.assertEqual(cc[key].name, key)

    @unpack
    @data(
        { 'key': 'k', 'names': ['a', 'b', 'c', 'k']},
        { 'key': 'a', 'names': ['a']}
    )
    def test_contains(self, key, names):
        cells = [fp.Cell(name) for name in names]
        cc = fp.CellContainer(self.NAME, cells)
        self.assertTrue(cc.contains(key))

    @unpack
    @data(
        { 'key': 'z', 'names': ['a', 'b', 'c', 'k']},
        { 'key': 'A', 'names': ['a']}
    )
    def test_getitem_assert(self, key, names):
        cells = [fp.Cell(name) for name in names]
        cc = fp.CellContainer(self.NAME, cells)
        self.assertRaises(KeyError, lambda: cc[key])

    @unpack
    @data(
        { 'key': 'z', 'names': ['a', 'b', 'c', 'k']},
        { 'key': 'A', 'names': ['a']}
    )
    def test_not_contains(self, key, names):
        cells = [fp.Cell(name) for name in names]
        cc = fp.CellContainer(self.NAME, cells)
        self.assertFalse(cc.contains(key))

    def test_getitem_same(self):
        cells = [fp.Cell('cell'), fp.Property('prop', 1)]
        cc = fp.CellContainer(self.NAME, cells)
        for cell in cells:
            key = cell.name
            self.assertEqual(cell, cc['*'+key])

    def test_not_contains_own_name(self):
        names = ['a', 'b', 'c', 'd']
        cells = [ fp.Cell(name) for name in names ]
        cc = fp.CellContainer('name', cells)
        self.assertFalse(cc.contains('name'))

    def test_keys(self):
        names = ['a', 'z', '111', 'b', 'lorem ipsum']
        cells = [fp.Cell(name) for name in names]
        cc = fp.CellContainer(self.NAME, cells)
        self.assertEqual(cc.keys(), names)

    def test_values(self):
        names = ['a', 'z', '111', 'b', 'lorem ipsum']
        cells = [fp.Cell(name) for name in names]
        cc = fp.CellContainer(self.NAME, cells)
        self.assertEqual(cc.values(), cells)

    def test_prop_value(self):
        p1 = fp.Property('p1', 1)
        p2 = fp.Property('p2', 2)
        cells = [p1, p2]
        cc = fp.CellContainer(self.NAME, cells)
        self.assertEqual(cc['p1'], 1)
        self.assertEqual(cc['p2'], 2)

    def test_prop_value_append(self):
        cc = fp.CellContainer(self.NAME, [])

        p = fp.Property('p', 1)
        cc.append(p)
        self.assertEqual(cc['p'], 1)

    def test_prop_value_changed(self):
        p1 = fp.Property('p1', 1)
        p2 = fp.Property('p2', 2)
        cells = [p1, p2]
        cc = fp.CellContainer(self.NAME, cells)
        p2.value = 22
        self.assertEqual(cc['p1'], 1)
        self.assertEqual(cc['p2'], 22)

    def test_prop_value_change_inside(self):
        p1 = fp.Property('p1', 1)
        p2 = fp.Property('p2', 2)
        cells = [p1, p2]
        cc = fp.CellContainer(self.NAME, cells)
        cc['p1'] = 11
        self.assertEqual(p1.value, 11)
        self.assertEqual(p2.value, 2)

    def test_prop_value_changed_attr(self):
        p1 = fp.Property('p1', 1)
        p2 = fp.Property('p2', 2)
        cells = [p1, p2]
        cc = fp.CellContainer(self.NAME, cells)
        p2.value = 22
        self.assertEqual(cc.p1, 1)
        self.assertEqual(cc.p2, 22)

    def test_prop_value_change_inside_attr(self):
        p1 = fp.Property('p1', 1)
        p2 = fp.Property('p2', 2)
        cells = [p1, p2]
        cc = fp.CellContainer(self.NAME, cells)
        cc.p1 = 11
        self.assertEqual(p1.value, 11)
        self.assertEqual(p2.value, 2)

    def test_prop_value_changed_priv(self):
        p1 = fp.Property('p1', 1)
        p2 = fp.Property('p2', 2)
        cells = [p1, p2]
        cc = fp.CellContainer(self.NAME, cells)
        p2.value = 22
        self.assertEqual(cc['*p1'].value, 1)
        self.assertEqual(cc['*p2'].value, 22)

    def test_prop_value_change_inside_priv(self):
        p1 = fp.Property('p1', 1)
        p2 = fp.Property('p2', 2)
        cells = [p1, p2]
        cc = fp.CellContainer(self.NAME, cells)
        cc['*p1'].value = 11
        self.assertEqual(p1.value, 11)
        self.assertEqual(p2.value, 2)

    def test_prop_appended_value_changed(self):
        cc = fp.CellContainer(self.NAME, [])
        p = fp.Property('p', 1)
        cc.append(p)

        self.assertEqual(cc['p'], 1)
        p.value = 2
        self.assertEqual(cc['p'], 2)

    def test_prop_value_changed_getitem_priv(self):
        cc = fp.CellContainer(self.NAME, [])
        p = fp.Property('p', 1)
        cc.append(p)

        cc['*p'].value = 3
        self.assertEqual(p.value, 3)

    def test_prop_value_changed_getitem_value(self):
        cc = fp.CellContainer(self.NAME, [])
        p = fp.Property('p', 1)
        cc.append(p)

        cc['p'] = 4
        self.assertEqual(p.value, 4)

    def test_prop_value_changed_attr_value(self):
        cc = fp.CellContainer(self.NAME, [])
        p = fp.Property('p', 1)
        cc.append(p)

        cc.p = 5
        self.assertEqual(p.value, 5)

    def test_append(self):
        sc_names = ['1', '2']
        starting_cells = [fp.Cell(name) for name in sc_names]

        ac_names = ['3', '4', self.NAME]
        cells_to_append = [fp.Cell(name) for name in ac_names]

        cc = fp.CellContainer(self.NAME, starting_cells)
        for cell in cells_to_append:
            cc.append(cell)

        for name in sc_names+ac_names:
            self.assertTrue(cc.contains(name))

    def test_append_fails(self):
        sc_names = ['1', '2']
        starting_cells = [fp.Cell(name) for name in sc_names]

        from copy import deepcopy
        ac_names = deepcopy(sc_names)
        cells_to_append = [fp.Cell(name) for name in ac_names]

        cc = fp.CellContainer(self.NAME, starting_cells)
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

    def test_getattribute_value(self):
        p1 = fp.Property('p1', 1)
        p2 = fp.Property('p2', 2)
        cc = fp.CellContainer(self.NAME, [p1, p2])
        self.assertEqual(cc.p1, p1.value)
        self.assertEqual(cc.p2, p2.value)

        p1.value = 3
        p2.value = 4
        self.assertEqual(cc.p1, p1.value)
        self.assertEqual(cc.p2, p2.value)


    def test_getattribute_attr(self):
        p1 = fp.Property('p1', 1)
        p2 = fp.Property('p2', 2)
        cc = fp.CellContainer(self.NAME, [p1, p2])
        self.assertEqual(cc['*p1'], p1)
        self.assertEqual(cc['*p2'], p2)

        p1.value = 3
        p2.value = 4
        self.assertEqual(cc['*p1'], p1)
        self.assertEqual(cc['*p2'], p2)


@ddt
class TestStrictCellContainer(unittest.TestCase):

    @data(
        [],
        [fp.Cell('a')],
        [fp.Cell('a'), fp.Cell('b')]
    )
    def test_constructor(self, cells):
        try:
            scc = fp.StrictCellContainer('n', cells)
        except Exception as e:
            self.fail('Exception: {}'.format(str(e)))

    @data(
        [fp.Cell('a'), fp.Cell('a')],
        [fp.Cell('a'), fp.Property('b', 1)],
        [fp.Property('a', 1)],
        [fp.PropertyInt('a', 2)]
    )
    def test_constructor_exception(self, cells):
        try:
            scc = fp.StrictCellContainer('n', cells)
        except ValueError:
            pass
        except Exception as e:
            self.fail('Wrong Exception: {}!'.format(str(e)))
        else:
            self.fail('Exception not occured for {}!'.format(cells))

    @data(fp.Cell('a'))
    def test_append(self, cell):
        scc = fp.StrictCellContainer('n', [fp.Cell('x')])
        try:
            scc.append(cell)
        except Exception as e:
            self.fail('Exception: {}'.format(str(e)))

    @data(
        fp.Cell('x'),
        fp.Property('b', 1),
        fp.PropertyInt('a', 2)
    )
    def test_append_exception(self, cell):
        scc = fp.StrictCellContainer('n', [fp.Cell('x')])
        try:
            scc.append(cell)
        except ValueError:
            pass
        except Exception as e:
            self.fail('Wrong Exception: {}!'.format(str(e)))
        else:
            self.fail('Exception not occured for {}!'.format(cell))


class TestLambda(unittest.TestCase):

    def setUp(self):
        self.lam1 = fp.Lambda('name', lambda: 1)

        self.x = -13
        self.lam_x = fp.Lambda('name', lambda: self.x)

        self.prop = fp.PropertyFloat('name', 1.3)
        self.lam_prop = fp.Lambda('name', lambda: self.prop.value)

    def test_constructor(self):
        pass

    def test_lambda_1(self):
        self.assertEqual(self.lam1.value, 1)

    def test_lambda_and_attribute(self):
        self.assertEqual(self.lam_x.value, self.x)

    def test_lambda_and_prop(self):
        self.assertEqual(self.lam_prop.value, self.prop.value)



@ddt
class TestProperty(unittest.TestCase):

    name = 'name'
    DEFAULT_VALUE = 0
    PROPER_VALUES = [1, 1., 'value', fp.Cell('name')]
    WRONG_VALUES = [None]
    TYPE = fp.Property
    TYPE_NAME = 'variant'

    def test_constructor(self):
        for proper_value in self.PROPER_VALUES:
            cell = self.TYPE(self.name, proper_value)
            # try:
            #     cell = self.TYPE(self.name, proper_value)
            # except Exception as e:
            #     # e = sys.exc_info()[0]
            #     self.fail('constructor failed for name {} and value {} ({})'
            #               .format(self.name, proper_value, e))

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
        for wrong_value in self.WRONG_VALUES:
            try:
                cell = self.TYPE(self.name, wrong_value)
            except ValueError:
                pass
            else:
                self.fail('<{}>: no value raise for value = {}!'
                        .format(cell, wrong_value))

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

    def test_writeable(self):
        for v in self.PROPER_VALUES:
            writeable_cell = self.TYPE(self.name, self.DEFAULT_VALUE, w=True)
            self.assertEqual(writeable_cell.writeable, True)
            try:
                writeable_cell.value = v
            except ValueError as e:
                self.fail('should be writeable: {} := {}, exception: {}'
                        .format(writeable_cell, v, e))
            except Exception as e:
                self.fail('unknown error: {}'.format(e))

    def test_not_writeable(self):
        for v in self.PROPER_VALUES:
            not_writeable_cell = self.TYPE(self.name, self.DEFAULT_VALUE, w=False)
            self.assertEqual(not_writeable_cell.writeable, False)
            try:
                not_writeable_cell.value = v
            except RuntimeError as e:
                pass  # ok
            except Exception as e:
                self.fail('unknown error: {}'.format(e))
            else:
                self.fail('Been able to write to not writeable cell!')

    def test_readable(self):
        readable_cell = self.TYPE(self.name, self.DEFAULT_VALUE, r=True)
        self.assertEqual(readable_cell.readable, True)
        try:
            some_val = readable_cell.value
        except RuntimeError as e:
            self.fail('should be readable: {}'.format(e))
        except Exception as e:
            self.fail('unknown error: {}'.format(e))

    def test_not_readable(self):
        not_readable_cell = self.TYPE(self.name, self.DEFAULT_VALUE, r=False)
        self.assertEqual(not_readable_cell.readable, False)
        try:
            some_val = not_readable_cell.value
        except RuntimeError as e:
            pass  # ok
        except Exception as e:
            self.fail('unknown error: {}'.format(e))
        else:
            self.fail('should not be readable')

    def test_not_execitable(self):
        not_executable_cell = self.TYPE(self.name, self.DEFAULT_VALUE)
        try:
            not_executable_cell()
            self.assertEqual(not_readable_cell.executable, False)
        except RuntimeError as e:
            pass
        except Exception as e:
            self.fail('unknown error: {}'.format(e))
        else:
            self.fail('cell is not executable, should raise!')

class TestPropertyInt(TestProperty):

    PROPER_VALUES = [-1, 0, 1,1000, '1']
    WRONG_VALUES = [-1.1, 0.1, 1.1, 'str']
    DEFAULT_VALUE = 0
    TYPE = fp.PropertyInt
    TYPE_NAME = 'int'

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
    TYPE = fp.PropertyFloat
    TYPE_NAME = 'float'


class TestPropertyString(TestPropertyInt):

    PROPER_VALUES = ['sting', 'long string \nlorem ipsum', u'unicode string',
            u'śćźżóęą']
    WRONG_VALUES = [(1,3), [1,2,3.4]]
    DEFAULT_VALUE = 's'
    TYPE = fp.PropertyString

@ddt
class TestPropertyEnum(unittest.TestCase):

    NAME = 'name'
    TYPE = fp.PropertyEnum
    TYPE_NAME = 'enum'

    # todo refactor
    def setUp(self):
        self.good_vals = ['a', 'b', 'c']
        self.init_val = self.good_vals[0]
        self.bad_vals = ['A', self.NAME, None, 0]
        options = [fp.Cell(v) for v in self.good_vals]

        self.enum = fp.PropertyEnum(self.NAME, options, self.init_val)

    @data(
        [fp.Cell('a')],
        [fp.Cell('a'), fp.Cell('b')]
    )
    def test_constructor(self, good_options):
        value = good_options[0].name
        try:
            enum = fp.PropertyEnum(self.NAME, good_options, value)
        except Exception as e:
            self.fail('Exception occured for name: {}, opts: {}, '
                      'val: {}: {}'
                      .format(self.NAME, good_options, value, str(e)))

    @data(
        [],
        [None],
        [fp.Cell('a'), 1],
        [fp.Cell('a'), fp.Cell('a')],
        [fp.Cell('a'), fp.Property('b',1)]
    )
    def test_constructor_exception(self, wrong_options):
        try:
            value = wrong_options[0].name
        except:
            value = None

        try:
            enum = fp.PropertyEnum(self.NAME, wrong_options, value)
        except ValueError:
            pass
        # except Exception as e:
        #     self.fail('Wrong exception!: {}, {}'.format(type(e), str(e)))
        else:
            self.fail('No exception for name: {}, wrong opts: {}, val: {}'
                    .format(self.NAME, wrong_options, value))

    @data('c', 'd', None, [], fp.Cell('a'))
    def test_constructor_wrong_values_exception(self, wrong_val):
        options = [fp.Cell('a'), fp.Cell('b')]

        try:
            enum = fp.PropertyEnum(self.NAME, options, wrong_val)
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


# TODO inherit from TestPropertyEnum ?
@ddt
class TestPropertyBool(TestProperty):

    PROPER_VALUES = ['True', 'False']
    WRONG_VALUES = [-1.1, 1, 'true']
    DEFAULT_VALUE = True
    TYPE = fp.PropertyBool
    TYPE_NAME = 'bool'

    @data(True, False)
    def test_additional_init_args(self, v):
        try:
            self.TYPE(self.name, v)
        except Exception as e:
            self.fail('cannot use {} as init argument for valu! exception:'
                    .format(v, e))

@ddt
class TestUnion(unittest.TestCase):

    NAME = 'name'
    TYPE = fp.Union
    TYPE_NAME = 'union'
    PROPER_VALUES = [
        {
            'a': [fp.Cell('a1'), fp.Cell('a2')],
            'b': [fp.Cell('b1')]
        }]

    def test_constructor(self):
        for type_map in self.PROPER_VALUES:
            try:
                union = fp.Union(self.NAME, type_map)
            except Exception as e:
                self.fail('Exception occured for name: {}, type_map: {}, '
                          ': {}'
                          .format(self.NAME, type_maplue, str(e)))

    def test_change_type(self):
        for type_map in self.PROPER_VALUES:
            union = fp.Union(self.NAME, type_map)

            try:
                for possible_type in type_map.keys():
                    union['type'].value = possible_type
            except KeyError() as e:
                self.fail('Exception occured for type {} : {}'
                        .format(possible_type, e))


    def test_change_type(self):
        type_map = self.PROPER_VALUES[0]
        bad_types = ['c', 'A', 'aa']
        union = fp.Union(self.NAME, type_map)

        for bad_type in bad_types:
            try:
                union.type = bad_type
            except ValueError as e:
                pass
            else:
                self.fail('Exception NOT occured for type {} : {}'
                        .format(possible_type, e))


    def test_change_childs_value(self):
        v1 = 1
        propInt = fp.PropertyInt('b', v1)
        type_map = {
                'a': [propInt]
            }
        union = fp.Union(self.NAME, type_map)
        # initial check
        self.assertEqual(v1, union.b)
        self.assertEqual(propInt, union['*b'])

        v2 = 2
        self.assertNotEqual(v1, v2)

        # change and check
        union.b = v2
        self.assertEqual(v2, union.b)
        self.assertEqual(propInt.value, union.b)
        self.assertEqual(propInt, union['*b'])



if __name__ == '__main__':
    unittest.main()
