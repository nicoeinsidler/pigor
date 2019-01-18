#!/usr/bin/env python3

import re
import numpy as np
import matplotlib.pyplot as plt
import os.path
from datetime import datetime
from pathlib import Path
# from scipy.optimize import curve_fit

class Measurement:
    """
    This class provides an easy way to read, analyse and plot data from 
    text files.
    """

    def __init__(self, path, type_of_measurement="default", type_of_fit="gauss"):
        """
        The Measurement class provides an easy and quick way to read, 
        analyse and plot data from text files. When creating a new instance,
        the following parameters have to be provided:

            :param self:        the object itself
            :param path:        pathlib.Path object

        Returns nothing.
        """
        # sets the number of lines of header of file (line 0 to N_HEADER)
        self.N_HEADER = 4

        self.path = path

        # change measurement type
        self.type_of_measurement     = type_of_measurement
        # change type of fit
        self.type_of_fit             = type_of_fit

        self.fit_function_list = {
             'gauss'     :   self.gauss,
             'sine'      :   self.sine,
             'sine_sin'  :   self.sine_lin,
             'poly5'     :   self.poly5
        }

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
        
    def detect_measurement_type(self):
        
        # if DC#X scan
        if re.match(r"[0-9]{4}_[0-9]{2}_[0-9]{2}_[0-9]{4}_[dD][cC][0-9][xX]", self.path.name):

            self.type_of_measurement = "DC"
            self.type_of_fit = "sine_lin"
            self.settings['DC Coil Axis'] = "X"

            # get the number of the DC coil
            match = re.search(r"(?i)dc(\d+)", self.path.name)
            if match:
                # write number into self.settings
                self.settings['DC Coil Number'] = match.group(1)

        # else if DC#Z scan
        elif re.match(r"[0-9]{4}_[0-9]{2}_[0-9]{2}_[0-9]{4}_[dD][cC][0-9][zZ]", self.path.name):

            self.type_of_measurement = "DC"
            self.type_of_fit = "poly5"
            self.settings['DC Coil Axis'] = "Z"

            # get the number of the DC coil
            match = re.search(r"(?i)dc(\d+)", self.path.name)
            if match:
                # write number into self.settings
                self.settings['DC Coil Number'] = match.group(1)

        # else if POS# scan
        elif re.match(r"[0-9]{4}_[0-9]{2}_[0-9]{2}_[0-9]{4}_[pP][oO][sS][0-9]", self.path.name):

            self.type_of_measurement = "POS"
            self.type_of_fit = "gauss"

            # get the number of the DC coil
            match = re.search(r"(?i)pos(\d+)", self.path.name)
            if match:
                # write number into self.settings
                self.settings['Linear Stage Axis'] = match.group(1)

        else:
            self.measurement_type()

        # if degree of polarization measurement
        if "pol" in self.path.name:
            self.type_of_measurement = "POS"
            self.type_of_fit = "gauss"
            self.degree_of_polarisation()


        # override type_of_fit if one of the key strings is matched
        for k, v in self.fit_function_list:
            if k in self.path.name: self.type_of_fit = k


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

        # detect type of measurement
        self.detect_measurement_type()
        

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

        # if measurement is degree of polarisation measurement
        if self.measurement_type == 'pol':
            self.degree_of_polarisation()
        else:
            self.select_columns()

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


    def degree_of_polarisation(self):
        # select default columns
        self.select_columns()

        # helper vars for raw data
        raw_x = self.x
        raw_y = self.y

        # set y axis values
        self.y = raw_y[::4]

        # calculation of degree of polarization and its error
        self.x = [raw_x[i] + raw_x[i+1] + raw_x[i+2] for i in range(0, len(raw_x), 4)] # TODO adding formular for degree of pol
        self.x_error = [np.sqrt(raw_x[i]) + raw_x[i] + raw_x[i] for i in range(0, len(raw_x), 4)] # TODO adding formular for error degree of pol



    # def fit(self, fit_function=None):

    #     if fit_function == None:
    #         fit_function = self.fit_function_list[self.type_of_measurement]

    #     return curve_fit(self.)
        
    def select_columns(self, column1=(0,1), column2=(1,1)):
        self.x = self.data[::column1[1],column1[0]]
        self.y = self.data[::column2[1],column2[0]]

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

        # create label
        title = self.path.name + "\n" + type_of_plot + self.settings['timestamp'].strftime("%Y-%m-%d %H:%M")

        # plot title
        plt.title(title)

        # axes labels
        plt.xlabel(self.desc[column1[0]])
        plt.ylabel(self.desc[column2[0]])

        # plot
        plt.plot(self.x,self.y)

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

    def gauss(self, x, a, x0, sigma):
        """
        Gaussian function, used for fitting data.

            :param x:       parameter
            :param a:       amplitude
            :param x0:      maximum
            :param sigma:   width
        """
        return a*np.exp(-(x-x0)**2/(2*sigma**2))

    def sine_lin(self):
        print('not yet implemented')

    def poly5(self):
        print('not yet implemented')

    def sine(self):
        print('not yet implemented')
    


# here you can test the class
if __name__ == "__main__":
    msrmt = Measurement(Path("./testfiles/2018-12-11-1000-dc1com.dat"))
    msrmt.plot()
