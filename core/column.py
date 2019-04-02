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
        
        """
        self.data.append(element)



if __name__ == "__main__":
    import doctest
    doctest.testmod()
