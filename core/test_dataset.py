#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import column
import dataset
import numpy as np


class TestDataSet(unittest.TestCase):
    def setUp(self):
        """Setting up some DataSet instances to test with"""
        self.a = dataset.DataSet([[1,2,3],[1,2,3]])


    def test_insufficient_args(self):
        """Make sure type or value errors are raised when necessary"""
        # arg must be list
        self.assertRaises(TypeError, dataset.DataSet, 1)
        self.assertRaises(TypeError, dataset.DataSet, True)
        self.assertRaises(TypeError, dataset.DataSet, {})
        self.assertRaises(TypeError, dataset.DataSet, 'test')

        # list must contain at least 2 entries
        self.assertRaises(ValueError, dataset.DataSet, [])
        self.assertRaises(ValueError, dataset.DataSet, [1])
        self.assertRaises(ValueError, dataset.DataSet, ['test'])

        # lists in data must be list, np.ndarray, np.array or Column
        self.assertRaises(ValueError, dataset.DataSet, [1, 2])
        self.assertRaises(ValueError, dataset.DataSet, ['test', 'test'])
        self.assertRaises(ValueError, dataset.DataSet, [{}, {}])
        self.assertRaises(ValueError, dataset.DataSet, [True, False])

        # all lists in data must be of same type
        self.assertRaises(TypeError, dataset.DataSet, [[1,2], column.Column('test', [1,2])])
        self.assertRaises(TypeError, dataset.DataSet, [[1,2], np.zeros(2)])

        # desc must be a string
        self.assertRaises(TypeError, dataset.DataSet, [[1,2],[2,3]], 1)
        self.assertRaises(TypeError, dataset.DataSet, [[1,2],[2,3]], True)
        self.assertRaises(TypeError, dataset.DataSet, [[1,2],[2,3]], ['test'])
        self.assertRaises(TypeError, dataset.DataSet, [[1,2],[2,3]], {})
        self.assertRaises(TypeError, dataset.DataSet, [[1,2],[2,3]], [])


    def test_len(self):
        """Make sure that __len__ is working properly."""
        self.assertEqual(len(self.a), 2)