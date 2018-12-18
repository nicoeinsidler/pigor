#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
import os.path
from datetime import datetime
from pathlib import Path

class Measurement:
    """
    This class provides an easy way to read, analyse and plot data from 
    text files.
    """

    def __init__(self, path, type_of_measurement="default"):
        """
        The Measurement class provides an easy and quick way to read, 
        analyse and plot data from text files. When creating a new instance,
        the following parameters have to be provided:

            :param self:        the object itself
            :param directory:   the directory of the file to read data from
            :param file_name:   the name of the file to read from (containing
                                also its file extention)

        Returns nothing.
        """
        # sets the number of lines of header of file (line 0 to N_HEADER)
        self.N_HEADER = 4

        self.path = path

        self.type_of_measurement = type_of_measurement

        # try to read the data
        try:
            self.read_data(path)
        except IOError as e20:
            print(e20)
        except Exception as e:
            print(e)

        # try to cleanup the data
        try:
            self.clean_data()
        except Exception as e:
            print(e)
    
    def measurement_type(self, type_of_measurement="default"):
        """
        Sets the type of the measurement if parameter type_of_measurement is set.

            :param self:                            object itself
            :param type_of_measurement="default":   new type of measurement

        Returns the current type of measurement.
        """
        if type_of_measurement != "default":
            self.type_of_measurement = type_of_measurement

        return self.type_of_measurement
        

    def read_data(self, path):
        """
        Reads data from file and stores it in the object.

            :param self:        the object itself
            :param directory:   the directory of the file to read data from
            :param file_name:   the name of the file to read from (containing
                                also its file extention)
        
        Returns nothing if successfull, but rasies exception if not.
        """

        # import the data
        self.raw = [line.rstrip('\n') for line in open(path)]
        

    def clean_data(self):
        """
        Splits the raw data into head and data vars.
        """

        # get the first lines for the header and split the lines by pipe char
        self.head = [line.split('|') for line in self.raw[0:self.N_HEADER]]
        # get rest of the file and cast all numbers to float, then create numpy array
        self.data = np.array([[float(number) for number in line.split()] for line in self.raw[self.N_HEADER+1:-1]])
        # get last line of head for axis labels for plots
        self.desc = [' '.join(item) for item in [item.split() for item in [item.split(": ") for item in self.head[-1]][0]]]

        try:
            self.settings = {
                'timestamp'      : datetime.strptime(self.head[0][0].split()[-1], '%d/%m/%Y@%H:%M')
            }
            i = 0
            for line in self.head:
                for item in line:
                    i += 1
                    l = item.split(":")
                    if i != 1:
                        self.settings[l[0]] = l[1]
        except Exception as e:
            print(e)

        


    def plot(self, column1=(0,1), column2=(1,1), fit=True, type_of_plot="", override=True):
        """
        Creates a plot for the data. If fit is set to False the data fit won't be
        plotted, even if there exists one. Following parameters are possible:

            :param self:            the object itself
            :param column1=(0,1):   (column, nth element) to choose the data from for x-axis
            :param column2=(1,1):   (column, nth element) to choose the data from for y-axis
            :param fit=True:        if set to False plotting of the fit will be supressed
            :param type_of_plot="": string to specify a certain plot type, which will be used
                                    in the file name as well as in the plot title
            :param override=True:   determines if plot image should be recreated if it
                                    already exists

        """

        # select the data to plot
        x = self.data[::column1[1],column1[0]]
        y = self.data[::column2[1],column2[0]]


        # create label
        title = self.path.name + "\n" + type_of_plot + self.settings['timestamp'].strftime("%Y-%m-%d %H:%M")

        # plot title
        plt.title(title)

        # axes labels
        plt.xlabel(self.desc[column1[0]])
        plt.ylabel(self.desc[column2[0]])

        # plot
        plt.plot(x,y)

        # file name
        if type_of_plot != "":
            n = str(self.path.parent) + "/" + self.path.stem + "[" + type_of_plot + "].png"
        else:
            n = str(self.path.parent) + "/" + self.path.stem + ".png"

        #if (override == False and not os.path.isfile(n)):
            # save plot to file
        plt.savefig(n)

        # clear figure/plot for next
        plt.clf()



if __name__ == "__main__":
    msrmt = Measurement(Path("./testfiles/2018-12-11-1000-dc1com.dat"))
    msrmt.plot()
