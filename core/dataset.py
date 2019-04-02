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

        Example:

        >>> table = DataSet([[1,2,3],[4,5,6]])

        >>> table = DataSet([[1,2,3],[4,5,6]], desc='My Beautiful Table')

        >>> time = Column('Time', [12, 13, 14, 15, 16, 17, 18])
        >>> temp = Column('Temperature', [21.3, 21.6, 21.9, 22.5, 24.0, 24.3, 24.9])
        >>> heater = DataSet([time, temp], desc='Room Heater')
        
        """
        # test if data is a list
        if type(data) is not list:
            raise TypeError('Data must be a list.')

        # test if at least 2 lists in data
        if len(data) <= 1:
            raise ValueError('Data must contain at least two objects.')

        # test if lists in data are of valid types
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
        """Returns a human readable representation of the DataSet object as a string.
        
        
        Example:

        >>> time = Column('Time', [12, 13, 14, 15, 16, 17, 18])
        >>> temp = Column('Temperature', [21.3, 21.6, 21.9, 22.5, 24.0, 24.3, 24.9])
        >>> heater = DataSet([time, temp], desc='Room Heater')
        >>> print(heater)
        +----------------+
        |  Room Heater   |
        +----------------+
        |Time|Temperature|
        +----------------+
        |  12|       21.3|
        |  13|       21.6|
        |  14|       21.9|
        |  15|       22.5|
        |  16|       24.0|
        |  17|       24.3|
        |    (1 more)    |
        +----------------+


        .. todo:: if len(self.desc) > sum(l): alignment of data columns is off.

        """

        # array of strings that will be returned in the end
        s = []

        # determine the maximal lenght of each data list
        l_data = [max(list(map(len, list(map(str,d))))) for d in self.data]
        # get the max lenght of column descriptions and calculate lenght for string
        if type(self.data[0]) == Column:
            l_desc = [len(d.desc) for d in self.data]
            l = list(map(max, zip(l_data, l_desc)))
        else:
            l = l_data

        # lenght of table
        table_lenght = sum(l) + len(self.data) - 1

        # test if dataset has a description 
        try:
            self.desc

            # check lenght of desc
            if len(self.desc) > sum(l):
                table_lenght = len(self.desc) + len(self.data) - 1
            # create header
            header = f'|{self.desc:^{table_lenght}}|'
        except Exception:
            header = None
            pass


        # create optical divider
        divider = '+' + '-'*table_lenght + '+'

        if header:
            s.extend(
                [
                    divider,
                    header
                ]
            )

        # create column headers
        column_headers = '|'
        if type(self.data[0]) == Column:
            for lenght, d in zip(l, self.data):
                column_headers += f'{d.desc:^{lenght}}|'

        s.extend(
            [
                divider,
                column_headers,
                divider
            ]
        )


        # create string to show how many elements in one self.data entry
        more = f'({len(self.data[0])-6} more)'

        # create string to show some data
        data_t = list(zip(*self.data))
        for i, element in enumerate(data_t):
            buffer = '|'
            for lenght, entry in zip(l, element):
                buffer += f'{entry:>{lenght}}|'
            s.append(buffer)
            if i > 4:
                if not len(self.data[0]) == i+1:
                    s.append(f'|{more:^{table_lenght}}|')
                break
        s.append(divider)
        
        return '\n'.join(s)

    def __len__(self):
        """Returns the number of entries in :code:`data`.
        
        Example:

        >>> a = np.zeros(5)
        >>> b = np.zeros(5)
        >>> s = DataSet([a, b])
        >>> len(s)
        2

        """
        return len(self.data)
        

if __name__ == "__main__":
    import doctest
    doctest.testmod()
