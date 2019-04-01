#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import column

class TestColumn(unittest.TestCase):
    def test_insufficient_args(self):
        """Make sure type errors are raised when necessary"""
        # testing the parameter desc
        self.assertRaises(TypeError, column.Column, True, [1,2,3])
        self.assertRaises(TypeError, column.Column, 1, [1,2,3])
        self.assertRaises(TypeError, column.Column, 1.1, [1,2,3])
        self.assertRaises(TypeError, column.Column, [], [1,2,3])
        self.assertRaises(TypeError, column.Column, {}, [1,2,3])


        # testing the parameter data
        self.assertRaises(TypeError, column.Column, 'string', 'string')
        self.assertRaises(TypeError, column.Column, 'string', True)
        self.assertRaises(TypeError, column.Column, 'string', 1)
        self.assertRaises(TypeError, column.Column, 'string', 1.1)
        self.assertRaises(TypeError, column.Column, 'string', {'test' : 1})
        