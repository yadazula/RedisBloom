#!/usr/bin/env python
from rmtest import ModuleTestCase
from redis import ResponseError
import sys

if sys.version >= '3':
    xrange = range

class APBFTest(ModuleTestCase('../redisbloom.so')):
    def test_simple(self):
        self.cmd('flushall')
        items_list = ['AGE', 'PARTITIONED', 'BLOOM', 'FILTER']
        self.assertOk(self.cmd('apbf.reserve apbf 2 1000'))
        for i in range(len(items_list)):
            self.assertEqual('OK', self.cmd('apbf.insert apbf', items_list[i]))
        for i in range(len(items_list)):
            self.assertEqual([1L], self.cmd('apbf.query apbf', items_list[i]))
        self.assertEqual([0L], self.cmd('apbf.query apbf bloom'))

    def test_1expiry(self):
        tests = 10000
        self.cmd('flushall')
        self.assertOk(self.cmd('apbf.reserve apbf 2', tests))
        for i in range(tests * 2):
            self.assertEqual('OK', self.cmd('apbf.insert apbf', i))
        resp = []
        for i in range(int(tests * 1.1), tests * 2):
            resp.append(self.cmd('apbf.query apbf', i))
            #self.assertEqual([1L], self.cmd('apbf.query apbf', str(i)))
        expect_res = [[1L] for _ in range(int(tests * 0.9))]
        self.assertEqual(expect_res, resp)

        positive = 0
        for i in range(0, int(tests * 0.9)):
            positive += self.cmd('apbf.query apbf', i)[0]
        self.assertLess(positive / (tests * 0.9), 0.015)

if __name__ == "__main__":
    import unittest
    unittest.main()