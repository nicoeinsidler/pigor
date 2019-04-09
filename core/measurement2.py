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

        # save file_path internally
        self.file_path = file_path
        # save name internally if given
        if name:
            self.name = name

        # contains all fit models that are available to this instance
        self.fit_model_list = {}

        # read data from measurement file
        data = self.read()
        # create data frame from raw measurement data
        self.make_df(data)


    def make_df(self, raw: [list, list, list]):
        """Create a :class:`pandas.df` object from the raw data.
        
        .. todo:: Cover the cases where not enough column headers or too many are given.
        """

        # parse CSV files at default
        columns = [item for item in raw[1].split(',')]
        data = [[float(item) for item in line.split(',')] for line in raw[2]]
        

        # if column headers exist, use them and create data frame
        if raw[1] != []:
            self.data = pd.DataFrame.from_records(data, columns=columns)
        # no column headers exist, create data fram
        else:
            self.data = pd.DataFrame.from_records(data)


    def read(self) -> [list, list, list]:
        """Reads the file at :code:`self.file_path` and tries to differentiate between additional information and the actual measurement data. 

        Assumed file structure:

        - meta: additional information about the measurement;
        - head: column names for the data
        - data: the actual data points as numeric values
        

        After the files has been read and split, the three parts (meta, head and data) will be returned as 3 lists.

        .. todo:: This function still needs some love.

        """

        n_meta = -1

        # import the data
        raw = [line.rstrip('\n') for line in self.file_path.open()]

        # TODO: ugly cases
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
        # case: column headers are on first line
        elif n_meta == 0:
            return [
                [],
                raw[0],
                raw[1:]
            ]
        # general case
        else:
            return [
                raw[0:n_meta-1],
                raw[n_meta],
                raw[n_meta+1:]
            ]

    def plot(self):
        """Plots the data."""
        
        # set a plot title
        title = self.file_path.name

        print(dir(self))

        # size of output image in inches
        plt.figure(figsize=[9.71, 6])             

    


if __name__ == "__main__":
    t = Measurement('../testfiles/test.dat')
    t.read()

