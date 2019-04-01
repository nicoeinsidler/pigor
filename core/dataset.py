#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
from column import Column

class DataSet:
    """This class bundles data points stored as lists, np.array, np.ndarray
    or Column objects together in :code:`data` to form a meaningful data set.
    Additionally a :code:`desc` can be added to describe the data set.

    :code:`len(data) > 1` so that a DataSet object makes sense.

    In addition to that each data point list must be equal lenght. To ensure
    that, zeros are added to the lists with less entries.

    """
    
    def __init__(self, data, desc=None):
        """Initializes a DataSet object. It will ensure that the given data is a
        valid type and that every data point list is of equal lenght and type.
        
        Arguments:
            data {list} -- list of list, np.array, np.ndarray or Column objects of equal lenghts
        
        Keyword Arguments:
            desc {string} -- optional description of the data set (default: {None})
        """

        # test if at least 2 lists in data
        if len(data) <= 1:
            raise ValueError('Data must contain at least two objects.')

        # test if data is a list
        if type(data) is not list:
            raise TypeError('Data must be a list.')

        # test if lists of data are of valid types
        for d in data:
            if type(d) not in [list, np.array, np.ndarray, Column]:
                raise ValueError('Data must be a list of lists, np.array, np.ndarray or Column objects')

        # check if all lists of data have the same type
        if not len(set([type(d) for d in data])) == 1:
            raise TypeError('All entries of data must have the same type.')

        # max lenght of objects in data
        max_lenght = max(map(len, data))
        # make lists equal lenght
        for d in data:
            for _ in range(max_lenght - len(d)):
                d.append(0)

        # check desc to be a string
        if desc and type(desc) is not str:
           raise TypeError("The description must be a string.")

        # finally asign instance vars
        self.data = data
        if desc:
            self.desc = desc

        
    def __str__(self):
        """Returns a human readable representation of the DataSet object."""

        l_data = [max(list(map(len, str(d)))) for d in self.data]
        print(l_data)
        return str(l_data)

        

a = Column('first column', [1,2,3,4,5,6,7,8])
b = Column('second column', [1,2,3])
s = DataSet([a,b])
print(s)

s = DataSet([[1,2],[1,2,3,4,5]])
#print(s.data)
