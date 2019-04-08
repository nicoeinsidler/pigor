#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from measurement2 import Measurement
import pandas as pd
import numpy as np
import difflib
import emoji

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


    def read_pos_file(self):
        """Looks for a position file and reads it into :code:`pos_data`.
        
        .. todo:: When searching for a position file, the lenght of the file should match. So it should be at least 1/4 of the size of the original measurement file.
        .. todo:: When no match can be found, go one directory higher to look for a position file (this could be repeaded a few times).
        """
        # TODO: check if len(pos_data) == len(self.y every 4th) for even better matches

        # search for position file
        files = sorted(self.file_path.parent.rglob('*.pos'))

        # if there is only one file
        if len(files) == 1:
            self.pos_file_path = files[0]
            self.pos_data = [[float(number) for number in line.rstrip('\n').split('\t')] for line in self.pos_file_path.open()][0]
        # if there are more the closest will be chosen
        elif len(files) > 1:
            match = difflib.get_close_matches(self.file_path.name, files, n=1)

            if not match:
                self.pos_file_path = files[0]
            else:
                self.pos_file_path = match 
            
            self.pos_data = [[float(number) for number in line.rstrip('\n').split('\t')] for line in self.pos_file_path.open()][0]
        else:
            print(emoji.emojize(":red_book:  {}: No position file found.".format(self.file_path)))



    def degree_of_polarisation(self):
        """ Calculates the degree of polarisation for each position in :code:`pos_data`. """

        # helper vars for raw data
        raw_x = self.pos_data
        raw_y = self.data[self.data.columns[1]]


        if len(self.pos_data) == len(raw_x):
            # set x axis values from pos file
            x = self.pos_data[::4]
        elif len(self.pos_data) > len(raw_x):
            print(emoji.emojize(f':warning:  {self.file_path}: Position file lenght and data file lenght are not equal. Maybe wrong position file?'))
            # set x axis values from pos file anyway
            x = self.pos_data[::4][0:len(raw_x)//4]
        else:
            print(emoji.emojize(f':warning:  {self.file_path}: Could not use position file: Wrong position file!\nContinuing with arbitrary positions: 0 to 1 in {len(self.data)//4} steps.'))
            x = np.linspace(0, 1, len(raw_x)//4) # worst case


        # lenght of input data that will be used
        data_lenght = len(raw_y) - len(raw_y)%4

        # allocate arrays to fill later (faster when using numpy)
        y = np.zeros(data_lenght//4)
        y_error = np.zeros(data_lenght//4)

        for i in range(0, data_lenght, 4):
            a = raw_y[i+1]  # I_a
            b = raw_y[i+2]  # I_b
            c = raw_y[i+3]  # I_ab
            d = raw_y[i]    # I_off

            # some helper vars
            f1 = d-a
            f2 = d-b

            d2 = d**2

            p0 = f1*f2*(c*d-a*b)**3
            p1 = f2**2 * d2 * (c-b)**2
            p2 = f1**2 * f2**2 * d2
            p3 = f1**2 * d2 * (a-c)**2
            p4 = (a**2 * b + a*b * (b - c - 2*d) + c*d2)**2

            # calculation of degree of polarisation
            y[i//4] = np.sqrt(
                    np.abs((f1*f2)/(c*d-a*b))
                )

            # calculation of degree of polarisation error
            y_error[i//4] = 0.5 * np.sqrt(
                        np.abs((p1*a + p2*c + p3*b + p4*d) / p0)
                )

        self.dopd = pd.DataFrame.from_records(zip(y, y_error), columns=['Degree of Polarisation', 'Δ Degree of Polarisation'], index=x[0:len(y)])

        

if __name__ == "__main__":
    m = Polarimeter('../testfiles/polarimeter/2018-11-23-1545-scan-dc2x.dat', 'test polarimeter')
    #print(m.data)

    dop = Polarimeter('../testfiles/polarimeter/2018-11-22-1125-degree-of-polarisation.dat')
    dop.read_pos_file()
    dop.degree_of_polarisation()
    print(dop.dopd)


    """ if len(pos_data) == len(self.data):
            # set x axis values from pos file
            self.data.set_index(pos_data, inplace=True)
        elif len(pos_data) > len(self.data):
            print(emoji.emojize(f':warning:  {self.file_path}: Position file lenght and data file lenght are not equal. Maybe wrong position file?'))
            # set x axis values from pos file
            self.data.set_index(pos_data[::4][0:len(self.data)//4])
        else:
            print(emoji.emojize(f':warning:  {self.file_path}: Could not use position file: Wrong position file!\nContinuing with arbitrary positions: 0 to 1 in {len(self.data)//4} steps.'))
            self.data.set_index(np.linspace(0, 1, len(self.data)//4), inplace=True) # worst case
        #self.data.set_index(pos_data[::4], inplace=True) """
