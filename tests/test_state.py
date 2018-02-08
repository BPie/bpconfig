#encoding=utf-8

import sys
import unittest

from ddt import ddt, data, unpack

import figpie as fp
from figpie.state import State
from figpie.actions import ActionManager


@ddt
class TestState(unittest.TestCase):

    def setUp(self):
        lvl2 = fp.CellContainer('lvl2',
                [fp.Cell('2c1'),
                fp.Property('2p1', 1),
                fp.PropertyString('2p2', 'string')])
        lvl1 = fp.CellContainer('lvl1', [fp.Cell('1c2'), lvl2])
        root = fp.CellContainer('root', [fp.Cell('rc1'), lvl1])
        self.container = root
        self.actions = ActionManager()
        self.state = State(self.container, self.actions)

    @data(
        [],
        [fp.Cell('a'), fp.Property('b',1)],
    )
    def test_constructor(self, container):
        m = State(container, self.actions)

    @data(
        None,
        1,
        'some text'
    )
    def test_contstructor_raises(self, container):
        self.assertRaises(fp.WrongTypeException,
                lambda: State(container, self.actions))

    @data(
        [fp.Cell('a'), fp.Property('a',1)],
    )
    def test_contstructor_raises_same_name(self, container):
        self.assertRaises(fp.WrongNameException,
                lambda: State(container, self.actions))

    def test_current_root(self):
        self.assertEqual(self.state.current, self.container)

    def test_movement(self):

        def go_next(destination):
            self.state.go_next(destination)
            self.assertEqual(self.state.current.name, destination)

        def go_previous(compare):
            self.state.go_previous()
            self.assertEqual(self.state.current.name, compare)

        go_next('lvl1')
        go_next('lvl2')
        go_next('2c1')
        go_previous('lvl2')
        go_next('2p1')
        go_previous('lvl2')
        go_previous('lvl1')
        go_next('1c2')
        go_previous('lvl1')
        go_next('1c2')
        go_previous('lvl1')
        go_previous('root')
        go_next('rc1')
        go_previous('root')

    def test_go_down_in_root_raises(self):
        self.assertRaises(RuntimeWarning, lambda: self.state.go_previous())

    @data(
        'a',
        '1c2',
        'root',
        '2p2',
    )
    def test_go_up_raises(self, option):
        self.assertRaises(RuntimeWarning, lambda: self.state.go_next(option))

# @ddt
# class TestShortFinder(unittest.TestCase):

#     @unpack
#     @data(
#         (['abc', 'bxb', 'cxc'], ['a', 'b', 'c']),
#         (['a', 'aa', 'aaa'], ['a', 'A', '0']),
#         (['abc', 'abcd', 'abcde', 'a'], ['a', 'b', 'c', 'A']),
#     )
#     def testBasic(self, inp, expected_results):
#         results = menu.short_finder(inp)
#         for result, expected in zip(results, expected_results):
#             self.assertEqual(result, expected)


#     @unpack
#     @data(
#         (['adfc', 'bxb', 'cxc'], ['d', 'x', 'C'],['a', 'b', 'c']),
#         (['a', 'aa', 'aaa'], ['0', '1', '2'], ['a','A']),
#         (['a', 'aa', 'aaa'], ['a', 'A', '0'], ['abba'])
#     )
#     def testBanned(self, inp, expected_results, banned):
#         results = menu.short_finder(inp, banned=banned)
#         for result, expected in zip(results, expected_results):
#             self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
