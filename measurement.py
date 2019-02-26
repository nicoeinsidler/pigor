#!/usr/bin/env python3

import re
import numpy as np
import matplotlib.pyplot as plt
import os.path
from datetime import datetime
from pathlib import Path
from scipy.optimize import curve_fit

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
        # setting the fit resolution (how many points should be plotted)
        self.FIT_RESOLUTION = 2000

        self.path = path

        self.settings = {}

        # change measurement type
        self.type_of_measurement     = type_of_measurement
        # change type of fit
        self.type_of_fit             = type_of_fit

        # list of all available fitting functions with their default bounds
        self.fit_function_list = {
            'default'   :   (self.gauss, (-np.inf, np.inf)), # a, x0, sigma
            'gauss'     :   (self.gauss, (-np.inf, np.inf)), # a, x0, sigma
            'sine'      :   (self.sine, (-np.inf, np.inf)), #  a, omega, phase, c
            'sine_lin'  :   (self.sine_lin, (-np.inf, np.inf)), # a, omega, phase, c, b
            'poly5'     :   (self.poly5, (-np.inf,np.inf)) # a5, a4, a3, a2, a1, a0
        }


        # try to read the data
        try:
            self.read_data(self.path)
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
            #self.degree_of_polarisation()


        # override type_of_fit if one of the key strings is matched
        for k in self.fit_function_list:
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
            self.settings = {}
            print(e)


    def degree_of_polarisation(self):
        # select default columns
        self.select_columns()

        # helper vars for raw data
        raw_x = self.x
        raw_y = self.y

        # set x axis values
        self.x = raw_x[::4]

        # calculation of degree of polarization and its error
        self.y = [np.sqrt(((raw_y[i] - raw_y[i+1]) * (raw_y[i] - raw_y[i+2]))/(raw_y[i]*raw_y[i+3] - raw_y[i+1]*raw_y[i+2])) for i in range(0, len(raw_y), 4)]

        self.y_error = []
        for i in range(0, len(raw_y), 4):
            a = raw_y[i]    # I_a
            b = raw_y[i+1]  # I_b
            c = raw_y[i+2]  # I_ab
            d = raw_y[i+3]  # I_off

            # deviations
            da = np.sqrt[a]
            db = np.sqrt[b]
            dc = np.sqrt[c]
            dd = np.sqrt[d]

            # some helper vars
            f1 = d-a
            f2 = d-b

            d2 = d**2

            p0 = f1*f2*(c*d-a*b)**3
            p1 = f2**2 * d2 * (c-b)**2
            p2 = f1**2 * f2**2 * d2
            p3 = f1**2 * d2 * (a-c)**2
            p4 = (a**2*b + a*b * (b - c - 2*d) + c*d2)**2

            self.y_error.append(0.5 * (p1*da + p2*dc + p3*db + p4*dd) / p0)



    def fit(self, fit_function=None):

        # check if fit function is not explicitly set for fit()
        if fit_function == None:
            # default fit function for measurement type
            func = self.fit_function_list[self.type_of_fit]
            # try to find better bounds
            self.find_bounds(fit_function=self.type_of_fit)
        else:
            func = self.fit_function_list[fit_function]
            # try to find better bounds
            self.find_bounds(fit_function=fit_function)

        # write used fit_function for plotting
        self.used_fit_function = func

        # make a curve fit and save values
        self.popt, self.pcov = curve_fit(func[0], self.x, self.y, bounds=func[1], sigma=self.y_error, absolute_sigma=True)

        
    def select_columns(self, column1=(0,1), column2=(1,1)):
        self.x = self.data[::column1[1],column1[0]]
        self.y = self.data[::column2[1],column2[0]]

        self.y_error = np.sqrt(self.y)

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

        # plot fit if exists
        if fit == True and hasattr(self, 'used_fit_function'):
            x = np.linspace(self.x.min(), self.x.max(), self.FIT_RESOLUTION)
            plt.plot(x, self.used_fit_function[0](x, *self.popt), '-', label='fit')

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

    def sine_lin(self, x, a, omega, phase, c, b):
        """
        Sine function with linear term added for fitting data.
            :param self:   
            :param x:       parameter
            :param a:       amplitude
            :param omega:   frequency
            :param phase:   phase
            :param c:       offset
            :param b:       slope
        """   
        return a*np.sin(x*omega + phase) + b*x + c

    def poly5(self, x, a5, a4, a3, a2, a1, a0): # should be implemented as generalization of nth degree
        """Polynom 5th degree for fitting.
        
        Arguments:
            x -- parameter
            a5 -- coeff
            a4 -- coeff
            a3 -- coeff
            a2 -- coeff
            a1 -- coeff
            a0 -- coeff
        
        Returns:
            function -- polynomial 5th degree
        """
        return (((((a5*x + a4)*x + a3)*x + a2)*x + a1)*x + a0)

    def sine(self, x, a, omega, phase, c):
        """
        Sine function for fitting data.
            :param self:   
            :param x:       parameter
            :param a:       amplitude
            :param omega:   frequency
            :param phase:   phase
            :param c:       offset
        """   
        return a*np.sin(x*omega + phase) + c

    def find_bounds(self, fit_function=None):

        # check if fit function is not explicitly set for fit()
        if fit_function == None:
            # default fit function for measurement type
            func = self.type_of_fit
        else:
            func = fit_function

        print(func)

        # minima and maxima of x and y data
        x_min = self.x.min()
        x_max = self.x.max()
        y_min = self.y.min()
        y_max = self.y.max()

        # x data where y is max or min
        y_min_i = self.x[self.y.argmin()]
        y_max_i = self.x[self.y.argmax()]

        # cases for each type of fit
        if func == "gauss":
            # boundaries should be calculated here TODO
            pass
        elif func == "sine":
            # calculation of amplitude
            a = 0.5 * abs(y_max - y_min)
            # guessing the offset
            c = y_min + a
            # guessing an omega
            omega = np.pi / abs(y_max_i - y_min_i)
            # guessing a phase, works for now, but big values TODO
            phase = abs(y_max_i) + abs(y_min_i) / omega + np.pi/2

            # scale factor
            s = 0.5

            self.fit_function_list['sine'] = (
                self.sine, 
                (
                    [a - a*s, omega - omega*s, phase - phase*s, c - c*s], 
                    [a + a*s, omega + omega*s, phase + phase*s, c + c*s]
                )
            ) # a, omega, phase, c

        elif func == "sine_lin":
             # calculation of amplitude
            a = 0.5 * abs(y_max - y_min)
            # guessing the offset
            c = y_min + a
            # guessing an omega
            omega = np.pi / abs(y_max_i - y_min_i)
            # guessing a phase, works for now, but big values TODO
            phase = abs(y_max_i) + abs(y_min_i) / omega + np.pi/2
            # calculation of slope of linear term (sloppy TODO)
            b = abs(y_max - y_min) / abs(y_max_i-y_min_i)

            # scale factor
            s = 0.5

            print(
                [a - a*s, omega - omega*s, phase - phase*s, c - c*s, b - b*s], 
                [a + a*s, omega + omega*s, phase + phase*s, c + c*s, b + b*s]
            )

            self.fit_function_list['sine_lin'] = (
                self.sine_lin, 
                (
                    [a - a*s, omega - omega*s, phase - phase*s, c - c*s, - b*s], 
                    [a + a*s, omega + omega*s, phase + phase*s, c + c*s, + b*s]
                )
            ) # a, omega, phase, c, b

            
        elif func == "poly5":
            # TODO
            pass
        else:
            # rest bounds here useful?!
            pass
            
    def reset_bounds(self, fit_function=None):
        # check if fit function is not explicitly set for fit()
        if fit_function == None:
            # default fit function for measurement type
            func = self.type_of_fit
        else:
            func = fit_function

        self.fit_function_list[func][1] = (-np.inf, np.inf)


# here you can test the class
if __name__ == "__main__":
    print('Testing the Measurement Class')
    #m = Measurement(Path("./testfiles/2018-11-23-1325-degree-of-pol.dat"))
    m = Measurement(Path("./testfiles/2019_02_20_1340_dc2z_scan.dat"))
    m.find_bounds(fit_function='poly5')
    m.fit(fit_function='poly5')
    m.plot()
    
