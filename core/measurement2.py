#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import lmfit
import matplotlib.pyplot as plt
from pathlib import Path


class Measurement:
    """Bundles measurement data with fits, plots and other meta data."""


    def __init__(self, file_path, name=None):
        """Initializes a new Measurement instance.
        
        :param file_path: filepath to look for the data for; if the file does not exist, a ValueError is raised
        :type file_path: string or :class:`pathlib.Path`
        :param name: name of the measurement, defaults to None
        :param name: string, optional
        
        """

        # check if type of file_path is correct
        if not type(file_path) in [str, Path]:
            raise TypeError('file_path must be either a string or pathlib.Path.')
        # if file_path is string, convert to pathlib.Path
        if type(file_path) == str:
            file_path = Path(file_path)
        # check if file exists
        if not file_path.exists():
            raise ValueError('No file at file_path exists.')
        
        # check if name is a string
        if name and type(name) != str:
            raise TypeError('name must be a string.')


        self.file_path = file_path
        if name:
            self.name = name


    def read(self) -> [list, list, list]:
        """Reads the file at :code:`self.file_path` and tries to differentiate between additional information and the actual measurement data. 

        Assumed file structure:

        - meta: additional information about the measurement;
        - head: column names for the data
        - data: the actual data points as numeric values
        

        After the files has been read and split, the three parts (meta, head and data) will be returned as 3 lists.

        """

        n_meta = -1

        # import the data
        raw = [line.rstrip('\n') for line in open(self.file_path)]

        # go through lines and check if line starts with numeric
        for line in raw:
            if not line[0] in '0123456789+-.':
                n_meta +=1

        # case: no meta, no column head
        if n_meta == -1:
            return [
                [],
                [],
                raw
            ]
        elif n_meta == 0:
            return [
                [],
                raw[0],
                raw[1:]
            ]
        else:
            return [
                raw[0:n_meta-1],
                raw[n_meta],
                raw[n_meta+1:]
            ]
            


""" 
m = Measurement('../testfiles/polarimeter/2018-11-23-1545-scan-dc2x.dat')
print(m.read())

t = Measurement('./test.dat')
t.read() """