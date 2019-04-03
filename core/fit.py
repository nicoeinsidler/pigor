#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import lmfit
from column import Column


class Fit:
    """The :class:`fit.Fit` contains all the fit relevant methods
    and models. It can automatically find bounds and generate a fit."""

    list_of_models = {}

    def __init__(self, x, y, model='default'):
        """Initializes a :class:`Fit` object. x and y data must be provided
        and will be converted to Column objects.

        """

        # check if x and y have valid types
        valid_types = [list, np.array, np.ndarray, Column]
        if type(x) not in valid_types or type(y) not in valid_types:
            raise TypeError(f'x and y must be of type list, np.array, np.ndarray or Column object.')

        # assign self.x and self.y as Columns
        if type(x) is Column:
            self.x = x
        else:
            self.x = Column('x', x)
        if type(y) is Column:
            self.y = y
        else:
            self.y = Column('y', y)


