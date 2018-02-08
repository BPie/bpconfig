#encoding=utf-8

import sys
import unittest

from ddt import ddt, data, unpack

import figpie as fp


@ddt
class TestMenu(unittest.TestCase):

    def setUp(self):
        lvl2 = fp.CellContainer('lvl2',
                [fp.Cell('2c1'),
                fp.Property('2p1', 1),
                fp.PropertyString('2p2', 'string')])
        lvl1 = fp.CellContainer('lvl1', [fp.Cell('1c2'), lvl2])
        root = fp.CellContainer('root', [fp.Cell('rc1'), lvl1])
        self.container = root
        self.menu = fp.Menu(self.container)

    @data(
        [],
        [fp.Cell('a'), fp.Property('b',1)],
    )
    def test_constructor(self, container):
        m = fp.Menu(container)

    @data(
        [fp.Cell('a'), fp.Property('a',1)],
    )
    def test_contstructor_raises_name(self, container):
        self.assertRaises(fp.WrongNameException, lambda: fp.Menu(container))

    @data(
        None,
        1,
        'some text'
    )
    def test_contstructor_raises_type(self, container):
        self.assertRaises(fp.WrongTypeException, lambda: fp.Menu(container))

if __name__ == '__main__':
    unittest.main()
