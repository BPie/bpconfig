#encoding=utf-8

import sys
import unittest

from ddt import ddt, data, unpack

import figpie as fp
from figpie.shorts import ShortMapper, ShortFinder


@ddt
class TestShortMapper(unittest.TestCase):

    def setUp(self):
        self.mapper = ShortMapper()

    @unpack
    @data(
        (['abc', 'bxb', 'cxc'], ['a', 'b', 'c']),
        (['a', 'aa', 'aaa'], ['a', 'A', '0']),
        (['abc', 'abcd', 'abcde', 'a'], ['a', 'b', 'c', 'A']),
    )
    def testBasic(self, inp, expected_results):
        results = self.mapper(inp)
        for result, expected in zip(results, expected_results):
            self.assertEqual(result, expected)


    @unpack
    @data(
        (['adfc', 'bxb', 'cxc'], ['d', 'x', 'C'],['a', 'b', 'c']),
        (['a', 'aa', 'aaa'], ['0', '1', '2'], ['a','A']),
        (['a', 'aa', 'aaa'], ['a', 'A', '0'], ['abba'])
    )
    def testBanned(self, inp, expected_results, banned):
        results = self.mapper(inp, banned=banned)
        for result, expected in zip(results, expected_results):
            self.assertEqual(result, expected)


@ddt
class TestShortFinder(unittest.TestCase):

    def setUp(self):
        self.finder = ShortFinder()


    @unpack
    @data(
        (['a', 'aa', 'ba', 'A', ' a'],'a',['a', 'aa']),
        (['a', 'aa', 'aaba', 'abaa', 'Aa', ' aa'],'aa',['aa', 'aaba'])
    )
    def testBasicFind(self,shorts, sequence, expected_shorts):
        results = self.finder(shorts, sequence)
        for r in results:
            self.assertTrue(r in expected_shorts)
        self.assertEqual(len(results), len(expected_shorts))


if __name__ == '__main__':
    unittest.main()
