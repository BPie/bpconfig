import sys
import unittest

from ddt import ddt, data, unpack

import bpconfig.properties as props
import bpconfig.menu as menu


@ddt
class TestCell(unittest.TestCase):

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

    def test_current_root(self):
        self.assertEqual(self.menu._current, self.container)

    def test_movement(self):
        def go_up(destination):
            self.menu._go_up(destination)
            self.assertEqual(self.menu._current.name, destination)

        def go_down(compare):
            self.menu._go_down()
            self.assertEqual(self.menu._current.name, compare)

        go_up('lvl1')
        go_up('lvl2')
        go_up('2c1')
        go_down('lvl2')
        go_up('2p1')
        go_down('lvl2')
        go_down('lvl1')
        go_up('1c2')
        go_down('lvl1')
        go_up('1c2')
        go_down('lvl1')
        go_down('root')
        go_up('rc1')
        go_down('root')

    def test_go_down_in_root_raises(self):
        self.assertRaises(RuntimeWarning, lambda: self.menu._go_down())

    @data(
        'a',
        '1c2',
        'root',
        '2p2',
    )
    def test_go_up_raises(self, option):
        self.assertRaises(RuntimeWarning, lambda: self.menu._go_up(option))

