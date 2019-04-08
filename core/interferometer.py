#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from measurement2 import Measurement
import pandas as pd

class Interferometer(Measurement):
    """This class extends the Measurement class by adding some interferometer station specific methods.""" 

    def __init__(self, file_path, name=None):
        """Fire up :code:`__init__()` of :class:`measurement2.Measurement` and mold data into a :class:`pandas.df`."""
        
        super().__init__(file_path, name)
        self.make_df(self.read())

    def make_df(self, raw: [list, list, list]):
        """Create a :class:`pandas.df` object from the raw data."""

        # split header columns up
        columns = [item for item in raw[1].split('\t')]
        # cast strings to floats and split items in lines
        data = [[float(item) for item in line.split('\t')] for line in raw[2]]
        # create a new pandas data frame
        self.data = pd.DataFrame.from_records(data, columns=columns)


if __name__ == "__main__":
    m = Interferometer('../testfiles/interferometer/IFM_20190314_114454_180_Apert10x10.log', 'test interferometer')
    print(m.data)