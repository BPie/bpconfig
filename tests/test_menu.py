#encoding=utf-8

import sys
import unittest

from ddt import ddt, data, unpack

import bpconfig.properties as props
import bpconfig.menu as menu


@ddt
class TestMenu(unittest.TestCase):

    def setUp(self):
        lvl2 = props.CellContainer('lvl2',
                [props.Cell('2c1'),
                props.Property('2p1', 1),
                props.PropertyString('2p2', 'string')])
        lvl1 = props.CellContainer('lvl1', [props.Cell('1c2'), lvl2])
        root = props.CellContainer('root', [props.Cell('rc1'), lvl1])
        self.container = root
        self.menu = menu.Menu(self.container)

    @data(
        [],
        [props.Cell('a'), props.Property('b',1)],
    )
    def test_constructor(self, container):
        m = menu.Menu(container)

    @data(
        [props.Cell('a'), props.Property('a',1)],
        None,
        1,
        'some text'
    )
    def test_contstructor_raises(self, container):
        self.assertRaises(ValueError, lambda: menu.Menu(container))


if __name__ == '__main__':
    unittest.main()
