#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from measurement2 import Measurement
import pandas as pd

class Polarimeter(Measurement):
    """This class extends the Measurement class by adding some polarimeter station specific methods.""" 

    def __init__(self, file_path, name=None):
        """Fire up :code:`__init__()` of :class:`measurement2.Measurement` and mold data into a :class:`pandas.df`."""
        
        super().__init__(file_path, name)
        self.make_df(self.read())

    def make_df(self, raw: [list, list, list]):
        """Create a :class:`pandas.df` object from the raw data."""

        # split header columns up
        #columns = [i.strip() for i in raw[1].split(': ')] # TODO: Does not work, because Monitor_Max,Min (cnts/sec) are two columns
        columns = ['I Scan (mA)', 'Detector (cnts)', 'Monitor Max (cnts/sec)', 'Monitor Min (cnts/sec)', 'Norm(1/s)', 'err(1/s)', 'FlippRatio', 'ErrFlippRatio']
        # cast strings to floats and split items in lines
        data = [[float(item) for item in line.split()] for line in raw[2]]

        # create a new pandas data frame
        self.data = pd.DataFrame.from_records(data, columns=columns)

if __name__ == "__main__":
    m = Polarimeter('../testfiles/polarimeter/2018-11-23-1545-scan-dc2x.dat', 'test polarimeter')
    print(m.data)

