#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np

class Column:
    """This class is used to store some data array alongside its description in one object.
    
    .. todo:: implementing __add__
    .. todo:: implementing __sub__
    .. todo:: implementing __mul__
    .. todo:: implementing __pow__
    .. todo:: implementing __truediv__
    .. todo:: implementing __and__
    .. todo:: implementing __xor__
    .. todo:: implementing __or__
    .. todo:: implementing __abs__
    """

    def __init__(self, desc, data):
        """Init checks the type of desc and data and stores them in the object.
        
        :param desc:    a descriptive string for the data
        :param data:    a list containting some data
        
        Example:
        >>> c = Column('Average Temperatures',[23,23,22,23,21,24,30,31,32,28])


        Raises:
            TypeError -- if desc is not a string
            TypeError -- if data is not list, np.array or np.ndarray

        """

        if type(desc) is not str:
            raise TypeError("The description must be a string.")
        
        if type(data) not in [list, np.ndarray, np.array]:
            raise TypeError("The data must be a list or any numpy array.")

        self.desc = desc
        self.data = data

    def __repr__(self):
        """Returns a representation of the Column instance for developing purposes
        
        Example:
        >>> c = Column('Average Temperatures',[23,23,22,23,21,24,30,31,32,28])
        >>> c
        <Column class (desc=Average Temperatures, len(data)=10)>

        """
        return f'<Column class (desc={self.desc}, len(data)={len(self.data)})>'

    def __str__(self):
        """Returns a string showing the description and some data points.
        
        Example:
        >>> c = Column('Average Temperatures',[23,23,22,23,21,24,30,31,32,28])
        >>> print(c)
        +--------------------+
        |Average Temperatures|
        +--------------------+
        |                  23|
        |                  23|
        |                  22|
        |                  23|
        |                  21|
        |                  24|
        |      (4 more)      |
        +--------------------+

        """
        # create string to show how many elements
        more = f'({len(self.data)-6} more)'
        # get the maximal data lenght
        l_data = max(list(map(len,list(map(str, self.data)))))
        # get the maximal lenght of desc or data or more string
        l = max(len(self.desc), l_data)
        l = max(l, len(more))
        s = [
            '+' + '-'*l               + '+',
            '|' + f'{self.desc:^{l}}' + '|',
            '+' + '-'*l               + '+'
        ]
        for i, element in enumerate(self.data):
            # when getting tuples because of TypeErrors in __add__
            if type(element) == tuple:
                element = str(element)
            s.append(f'|{element:>{l}}|')
            if i > 4:
                if not len(self.data) == i+1:
                    s.append('|' + f'{more:^{l}}' + '|')
                break
        s.append('+' + '-'*l + '+')

        return '\n'.join(s)

    def __len__(self):
        """Returns the number of data points.
        
        Example:
        >>> c = Column('Average Temperatures',[23,23,22,23,21,24,30,31,32,28])
        >>> len(c)
        10

        """
        return len(self.data)

    def __iter__(self):
        """Defines an iterator for this class to make it iterable"""
        return iter(self.data)

    def append(self, element):
        """Appends an element to data.
        
        Example:
        >>> c = Column('Average Temperatures',[23,23,22,23,21,24,30,31,32,28])
        >>> c.append(27)
        >>> len(c)
        11

        >>> a = Column('a', [1,2])
        >>> a.append(5)
        >>> a.data
        [1, 2, 5]
        
        """
        self.data.append(element)

    def __getitem__(self, index):
        """Implements indexing: getting an item by index.

        Example:

        >>> a = Column('a', [1,2,3,4])
        >>> a[1]
        2
        """
        return self.data[index]

    def __setitem__(self, index, value):
        """Implements indexing: setting an item by index.

        Example:

        >>> a = Column('a', [1,2,3,4])
        >>> a[1] = 9
        >>> a.data
        [1, 9, 3, 4]

        """
        self.data[index] = value

    def __delitem__(self, index):
        """Implements indexing: deleting an item by index.

        Example:

        >>> a = Column('a', [1,2,3,4])
        >>> del a[0]
        >>> a.data
        [2, 3, 4]

        """
        del self.data[index]

    def __add__(self, other):
        """Implementing the + operator support to add the values of :code:`self.data`
        and :code:`other.data` per item.

        .. warning:: This operator works differently from how lists in python handle
        the + operator!

        .. note:: If unsupported operand types for + occur, a tuple is created to give
        the user the ability to deal with those conflicts later.

        Examples:

        Adding some two columns a and b, filled with integers. The integers will be
        added, whereas the description of the new column will be the old ones 
        separated by a + sign.

        >>> a = Column('a', [1,2,3])
        >>> b = Column('b', [2,2,2])
        >>> c = a + b
        >>> print(c)
        +---------+
        |  a + b  |
        +---------+
        |        3|
        |        4|
        |        5|
        +---------+

        Strings can also be added:

        >>> a = Column('a', ['str1'])
        >>> b = Column('b', ['str2'])
        >>> print(a + b)
        +---------+
        |  a + b  |
        +---------+
        | str1str2|
        +---------+

        If the + operator is not defined for the added values, a tuple is automatically
        created to give the user the ability to deal with those conflicts later.

        >>> a = Column('a', ['1'])
        >>> b = Column('b', [1])
        >>> print(a + b)
        +---------+
        |  a + b  |
        +---------+
        | ('1', 1)|
        +---------+

        """
        valid_types = [list, np.array, np.ndarray, Column]
        if type(other) not in valid_types:
            raise TypeError('You can only add objects of type list, np.array, np.ndarray or Column.')


        desc = self.desc + ' + ' + other.desc

        data1 = self.data
        if type(other) == Column:
            data2 = other.data
        else:
            data2 = other
        
        # extend data2 if needed
        if len(data1) > len(data2):
            data2.extend(
                [0 for _ in range(len(data1)-len(data2))]
            )
        # extend data1 if needed
        elif len(data1) < len(data2):
            data1.extend(
                [0 for _ in range(len(data2)-len(data1))]
            )

        # add values together
        data = []
        for a, b in zip(data1, data2):
            try:
                c = a + b
            except TypeError:
                c = (a,b)
            data.append(c)

        # return new Column object
        return Column(desc, data)

    def extend(self, l):
        """Extends :code:`self.data` by :code:`l`.
        
        Example:

        >>> a = Column('a', [1,2])
        >>> b = [3,4]
        >>> a.extend(b)
        >>> a.data
        [1, 2, 3, 4]

        >>> a = Column('a', [1,2])
        >>> b = Column('b', [3,4])
        >>> a.extend(b)
        >>> a.data
        [1, 2, 3, 4]

        """
        if type(l) == Column:
            self.data.extend(l.data)
        else:
            self.data.extend(l)


    def is_numeric(self):
        """Returns True if :code:`data` consists of only numeric values, else False.
        
        Examples:

        >>> a = Column('a', [1,2,3])
        >>> a.is_numeric()
        True

        >>> b = Column('b', [1,2,'3'])
        >>> b.is_numeric()
        False
        """
        if type(self.data) in [np.array, np.ndarray]:
            return np.isnan(self.data).any()
        else:
            s = set(map(type, self.data))
            if len(s) == 1 and list(s)[0] in [int, float]:
                return True
            else:
                return False





if __name__ == "__main__":
    import doctest
    doctest.testmod()
