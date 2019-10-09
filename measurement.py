#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import numpy as np
import matplotlib.pyplot as plt
import os.path
import glob
import difflib
from datetime import datetime
from pathlib import Path
from scipy.optimize import curve_fit
from markdown import markdown
from fit_functions import * # importing all the fit functions and decortator


try:
    import emoji
except Exception as e:
    print("Could not import package emoji. {}".format(e))

class Measurement:
    """This class provides an easy way to read, analyse and plot data from
    text files. 

    There are two different file formats, which are used on the interferometry
    as well as on the polarimeter station at Atominstitut of TU Wien. For more
    information on the conventions please head to the docs or take a look at
    the example files provided.

    """

    def __init__(self, path, type_of_measurement="default", type_of_fit="gauss"):
        """
        The Measurement class provides an easy and quick way to read, 
        analyse and plot data from text files. When creating a new instance,
        the following parameters have to be provided:

            :param self:                the object itself
            :param path:                pathlib.Path object
            :param type_of_measurement: used to hard set the type of measurement
                                        on instance creation (default value = 'default')
            :param type_of_fit:         sets an initial fit type, which may be overridden
                                        by detect_measurement_type() later (default value
                                        = 'gauss')
                                        TODO: change to be permanent?

        The startup sequence is as follows:

        1. try to read the data
        2. measurement type (either set it, when given as input argument or try to detect it)
        3. if measurement is POL, try to find a position file and read it
        4. clean up the given data
        5. select columns => write into self.x and self.y
        6. if measurement is POL, calculate degree of polarisation

        .. todo:: Is type_of_fit really needed?

        Returns nothing.
        """
        # sets the number of lines of header of file (line 0 to N_HEADER)
        self.N_HEADER = 4 #: number of lines of header of measurement file
        # setting the fit resolution (how many points should be plotted)
        self.FIT_RESOLUTION = 2000 #: number of points to calculate the fit for
        # which columns should be used for what measurement
        self.COLUMN_MAPS = {
            'default'   :   [('x',1),('y',1)],
            'POL'       :   [('x',1),('y',1)],
            'DC'        :   [('x',1),('y',1)],
            'rocking'   :   [('x',1),None,('y',1),('y',1),('y',1),('y',1)]
        }

        self.path = path #: path (pathlib.Path object) to the measurement file
        self.pos_file_path = None #: path (pathlib.Path object) to the corresponding position file

        self.settings = {} #: dict containing useful information read from files header in clean_data()

        
        # change type of fit
        self.type_of_fit = type_of_fit #: type of fit to be applied to the data

        # list of all available fitting functions with their default bounds
        global fit_function_list
        self.fit_function_list = fit_function_list #: list of fit functions that can be used; imported from fit_functions.py

        # starting init sequence -------------------------------

        # 1. try to read the data
        try:
            self.read_data(self.path)
            print(emoji.emojize(":open_book:  {}: Read data successfully.".format(self.path)))
        except IOError as e20:
            print(emoji.emojize(":red_book:  {}: {}".format(self.path,e20)))
        except Exception as e:
            print(emoji.emojize(":red_circle:  {}: {}".format(self.path,e)))


        # 2. measurement type
        if type_of_measurement != "default":
            # change measurement type
            self.type_of_measurement = type_of_measurement
        else:
            try:
                # auto detect which type of measurement
                self.detect_measurement_type()
                print(emoji.emojize(":white_heavy_check_mark:  {}: Detected measurement type {}.".format(self.path, self.type_of_measurement)))
            except Exception as e:
                print(emoji.emojize(":red_circle: {}: {}".format(self.path,e)))
        
        # 3. read position file if degree of polarisation measurement
        if self.type_of_measurement == "POL":
            # try to find a position file
            try:
                self.read_pos_file()
                print(emoji.emojize(":round_pushpin:  {}: Position file read: {}".format(self.pos_file_path, self.path)))
            except Exception as e:
                print(emoji.emojize(":red_circle:  {}: {}".format(self.path,e)))

        # 4. cleanup the data
        try:
            self.clean_data()
        except Exception as e:
            print(emoji.emojize(":red_circle:  {}: {}".format(self.path,e)))

        # 5. selecting columns and writing self.x & self.y
        try:
            self.select_columns(m=self.COLUMN_MAPS[type_of_measurement])
        except Exception as e:
            print(emoji.emojize(":red_circle:  {}: {}".format(self.path,e)))

        # 6. fire degree of polarisation if POL
        if self.type_of_measurement == 'POL':
            try:
                # calculate degree of polarisation
                self.degree_of_polarisation()
            except Exception as e:
                print(emoji.emojize(":red_circle:  {}: {}".format(self.path,e)))

        # end of init sequence -------------------------------


    def measurement_type(self, type_of_measurement="default"):
        """Sets the type of the measurement if parameter type_of_measurement is set.

        :param self:                            object itself
        :param type_of_measurement: default":   new type of measurement (default 
                                                value = 'default')
        
        Returns the current type of measurement.

        .. todo:: Evaluate if this method (measurement_type()) is needed at all.
        .. todo:: Set better default value for measurement type.

        """
        if type_of_measurement != "default":
            self.type_of_measurement = type_of_measurement
        else:
            # this is the default value of measurement type TODO: setting better default
            self.type_of_measurement = 'POS'

        return self.type_of_measurement
        
    def detect_measurement_type(self):
        """ This function auto detects the type of measurement based on the file
        name. This works best with a meaningful file name convention. For more
        information please refer to the docs.
        

        Several :code:`type_of_measurement` can be detected:

        - DC#X: x-field of DC coil number # scan -> sets :code:`type_of_fit = 'sine_lin'`
        - DC#Z: z-field of DC coil number # scan -> sets :code:`type_of_fit = 'poly5'`
        - POS: scan of different linear stage positions -> sets :code:`type_of_fit = 'gauss'`

        :code:`type_of_fit` can be overridden by explicitly mentioning a fit function to use
        in the name of the file. See docs for more information.

        In addition to the type of fit and measurement type, some additional
        information about the measurement is gathered in the :code:`settings` dict.

        """
        # if DC#X scan
        if re.search(r"(?i)dc[0-9][xX]", self.path.name):
            self.type_of_measurement = "DC"
            self.type_of_fit = "sine_lin"
            self.settings['DC Coil Axis'] = "X"

            # get the number of the DC coil
            match = re.search(r"(?i)dc(\d+)", self.path.name)
            if match:
                # write number into self.settings
                self.settings['DC Coil Number'] = match.group(1)

        # else if DC#Z scan
        elif re.search(r"(?i)dc[0-9][zZ]", self.path.name):

            self.type_of_measurement = "DC"
            self.type_of_fit = "poly5"
            self.settings['DC Coil Axis'] = "Z"

            # get the number of the DC coil
            match = re.search(r"(?i)dc(\d+)", self.path.name)
            if match:
                # write number into self.settings
                self.settings['DC Coil Number'] = match.group(1)

        # else if POS# scan
        elif re.search(r"(?i)pos[0-9]", self.path.name):

            self.type_of_measurement = "POS"
            self.type_of_fit = "gauss"

            # get the number of the DC coil
            match = re.search(r"(?i)pos(\d+)", self.path.name)
            if match:
                # write number into self.settings
                self.settings['Linear Stage Axis'] = match.group(1)

        # default case
        else:
            # if degree of polarization measurement
            if "pol" in self.path.name: 
                self.type_of_measurement = "POL"
                self.type_of_fit = "gauss"
            else:
                self.type_of_measurement = "POS"


        # override type_of_fit if one of the key strings is matched
        for k in self.fit_function_list:
            if k in self.path.name: self.type_of_fit = k


    def read_data(self, path):
        """Reads data from file and stores it in :code:`raw`.

        :param self: the object itself
        :param path: a pathlib.Path object pointing to a measurement file


        """

        # import the data
        self.raw = [line.rstrip('\n') for line in open(path)]

    def read_pos_file(self):
        """Looks for a position file and reads it into :code:`pos_data`.
        
        .. todo:: When searching for a position file, the lenght of the file should match. So it should be 1/4 of the size of the original measurement file.
        """
        # TODO: check if len(pos_data) == len(self.y every 4th) for even better matches

        # search for position file
        files = [Path(path) for path in glob.glob('**/*.pos', recursive=True)]

        # if there is only one file
        if len(files) == 1:
            self.pos_file_path = files[0]
            self.pos_data = np.array([[float(number) for number in line.rstrip('\n').split('\t')] for line in open(self.pos_file_path)][0])

        # if there are more the closest will be chosen
        elif len(files) > 1:
            match = difflib.get_close_matches(self.path.name, files, n=1)

            if not match:
                self.pos_file_path = files[0]
            else:
                self.pos_file_path = match 
            
            self.pos_data = np.array([[float(number) for number in line.rstrip('\n').split('\t')] for line in open(self.pos_file_path)][0])

        else:
            print(emoji.emojize(":red_book:  {}: No position file found.".format(self.path)))

        

    def clean_data(self):
        """Splits the :code:`raw` data into :code:`head` and :code:`data` vars."""

        # get the first lines for the header and split the lines by pipe char
        self.head = [line.split('|') for line in self.raw[0:self.N_HEADER]]
        # get rest of the file and cast all numbers to float, then create numpy array
        self.data = np.array([[float(number) for number in line.split()] for line in self.raw[self.N_HEADER:]])
        # get last line of head for axis labels for plots
        self.desc = [' '.join(item) for item in [item.split() for item in [item.split(": ") for item in self.head[-1]][0]]]


        # write information from head into settings
        self.settings = {}
        try:
            for line in self.head:
                for i, item in enumerate(line):
                    l = item.split(":")
                    if i != 0:
                        self.settings[l[0]] = l[1]
        except Exception as e:
            self.settings = {}
            print(emoji.emojize(":red_circle:  {}: {}".format(self.path, e)))

        
        # try to find measurement time stamp
        try:
            self.settings['time_stamp'] = datetime.strptime(self.head[0][0].split()[-1], '%d/%m/%Y@%H:%M')
        except:
            pass

        # try to find measurement time
        try:
            w = [
                'measurement time',
                'measure time',
                'time'
            ]
            for word in w:
                matches = difflib.get_close_matches(word, list(self.settings.keys()))
                if matches != []:
                    match = matches[0]
                    self.settings['measurement_time'] = int(re.search(r'\d+', self.settings[match]).group())
                    self.settings.pop(match)
                    break

        except:
            pass
        


    def select_columns(self, m=None):
        """ Selects columns of the :code:`data` as specified in m (map) and
        saves in :code:`x` and :code:`y[]`.

        ..note:: :code:`y_error[]` is calculated as sqrt(y)

        :param m:   map, e.g. list of tuples or None values; if m=None
                    select_columns will be skipped (Default value = None)
        
        The map :code:`m` definies which columns of the original measurement
        data will be used later. Only one x-axis can be defined, but multiple
        y-axes may be used. The lenght of the map must not exceed the number
        of the columns in :code:`data`, but can be less or equal.

        Each map is a list of items, which can either be tuples or None
        values, if a column should be skipped. In the case of a tuple, the
        first value must be a string, either 'x' or 'y', which determines
        if the column should be interpreted as an x- or y-axis. Its second
        value describes what nth element of the columns should be selected.

        A few examples:
        ::

            m = [('x',1),('y',1)]

        This will select the first column as x-axis and take every (1st)
        element of it, and the second column as y-axis, also using every
        element of that column.
        ::

            m = [('y',2),None,('x',2),('y',2)]

        Here we will take every second element of column 1, 3 and 4, but
        skip column 2.

        .. note:: If the lenght of the map is less than the number of columns in :code:`data`, every column that has no corresponding map element will be skipped.

        """

        if m == None:
            print('No map given!')
            raise AttributeError

        # transpose the data
        transposed_data = [list(i) for i in zip(*self.data)]

        # create lists
        self.y = list()
        self.y_error = list()
        # go through every column and every map item
        for map_item, column in zip(m, transposed_data):
            # if map item is None, skip
            if map_item and not column == []:
                # if this is x axis, write self.x
                if map_item[0] == 'x':
                    self.x = np.array(column[::map_item[1]])
                # if this is y axis, write new self.y and error
                elif map_item[0] == 'y':
                    self.y.append(np.array(column[::map_item[1]]))
                    self.y_error.append(np.array(np.sqrt(column[::map_item[1]])))

        


    def degree_of_polarisation(self):
        """ Calculates the degree of polarisation for each position in :code:`pos_data`. """

        # helper vars for raw data
        raw_x = self.x
        raw_y = self.y[0]


        if len(self.pos_data) == len(raw_x):
            # set x axis values from pos file
            self.x = self.pos_data[::4]
        elif len(self.pos_data) > len(raw_x):
            print(emoji.emojize(':warning:  {}: Position file lenght and data file lenght are not equal. Maybe wrong position file?'.format(self.path)))
            # set x axis values from pos file
            self.x = self.pos_data[::4][0:len(raw_x)//4]
        else:
            print(emoji.emojize(":warning:  {}: Could not use position file: Wrong position file!\nContinuing with arbitrary positions: 0 to 1 in {} steps.".format(self.path, len(raw_x)//4)))
            self.x = np.linspace(0, 1, len(raw_x)//4) # worst case


        # lenght of input data that will be used
        data_lenght = len(raw_y) - len(raw_y)%4

        # allocate arrays to fill later (faster when using numpy)
        self.y[0] = np.zeros(data_lenght//4)
        self.y_error[0] = np.zeros(data_lenght//4)

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
            self.y[0][i//4] = np.sqrt(
                    np.abs((f1*f2)/(c*d-a*b))
                )

            # calculation of degree of polarisation error
            self.y_error[0][i//4] = 0.5 * np.sqrt(
                        np.abs((p1*a + p2*c + p3*b + p4*d) / p0)
                )
            

    def fit(self, fit_function=None, fit_function_export=False):
        """ Fits the data in :code:`x` and :code:`y` using the default fit function of each
        :code:`type_of_fit` if not specified further by passing a certain fit function as an
        argument.

        :param fit_function:  fit function to use to fit the data with (Default value = None)
        :param fit_function_export: exports the fit function as a txt file in a specified format (Mathematica is default and only implementation yet.).

        Stores the optimal values and the covariances in :code:`popt` and :code:`pcov` for
        later use.

        """
        # check if fit function is not explicitly set for fit()
        if fit_function == None:
            # try to find better bounds
            self.find_bounds(fit_function=self.type_of_fit)
            # default fit function for measurement type
            func = self.fit_function_list[self.type_of_fit]
        else:
            # try to find better bounds
            self.find_bounds(fit_function=fit_function)

            func = self.fit_function_list[fit_function]

        # write used fit_function for plotting
        self.used_fit_function = func

        # create lists for fit
        self.popt, self.pcov = list(), list()
        for y, y_error in zip(self.y, self.y_error):
            # make a curve fit and save values
            popt, pcov = curve_fit(
                func[0], self.x, y,
                bounds=func[1],
                sigma=y_error,
                absolute_sigma=True
            )
            self.popt.append(popt)
            self.pcov.append(pcov)

        # if fit_function_export is set
        if fit_function_export != False:
            t = []
            for fit_param in self.popt:
                # check how many parameters the fit function expects
                func_param_number = len(func[0].__code__.co_varnames)
                
                # call fit function, but with export set
                t.append(func[0]('x', *fit_param[0:func_param_number-2], export="Mathematica"))
                t.append('\n')

            txtfile_name = self.path.with_name(self.path.stem + '_fit_functions.txt')
            with open(txtfile_name, 'w') as txtfile:
                for line in t:
                    txtfile.write('{}\n'.format(line))
            

    def plot(self, column1=(0,1), column2=(1,1), fit=True, type_of_plot='', override=True, file_extention='.png'):
        """Creates a plot for the data. If fit is set to False the data fit won't be
        plotted, even if there exists one. Following parameters are possible:

        :param self:            the object itself
        :param column1:         (column, nth element) to choose the data from for x-axis (Default value = (0)
        :param column2:         (column, nth element) to choose the data from for y-axis (Default value = (1)
        :param fit:             if set to False plotting of the fit will be supressed (Default value = True)
        :param type_of_plot:    string to specify a certain plot type, which will be used
                                in the file name as well as in the plot title (Default value = '')
        :param override:        determines if plot image should be recreated if it already exists (Default value = True)

        .. todo:: Make x and y labels more general, especially for interferometer files, where more that one y value list is needed.
        """
        
        # create label
        if 'time_stamp' in self.settings:
            title = self.path.name + '\n' + type_of_plot + '\n' + self.settings['time_stamp'].strftime("%Y-%m-%d %H:%M")
        else:
            title = self.path.name + "\n" + type_of_plot

        # size of output image in inches
        plt.figure(figsize=[9.71, 6])

        # plot title
        plt.title(title)

        # axes labels
        if self.type_of_measurement == 'POL':
            plt.xlabel('Position (steps)')
            plt.ylabel('Degree of Polarisation')
        else:
            # TODO: this is only valid if select_columns was used with default values!
            plt.xlabel(self.desc[column1[0]])
            plt.ylabel(self.desc[column2[0]])

        # get measurement time if available
        try:
            measurement_time = self.settings['measurement_time']
        except Exception as e:
            print(emoji.emojize(":red_circle:  {}: {}".format(self.path,e)))

        # plot
        for y, y_error in zip(self.y,self.y_error):
            plt.errorbar(self.x, y, yerr = y_error, label=f'data (Δt={measurement_time}s)')

        # plot fit if exists
        if fit == True:
            try:
                fit_function = self.used_fit_function
            except AttributeError:
                self.fit()
                fit_function = self.used_fit_function
            x = np.linspace(self.x.min(), self.x.max(), self.FIT_RESOLUTION)
            for i,popt in enumerate(self.popt):
                plt.plot(x, fit_function[0](x, *popt), '-', label=f'fit #{i}')

        # plot legend
        plt.legend()

        # all valid file extentions
        valid_file_extentions = [
            '.png',
            '.svg',
            '.eps',
            '.pdf'
        ]

        # make sure there is a point
        if not file_extention.startswith('.'):
            file_extention = '.' + file_extention

        # check if file extention is valid
        if not file_extention.casefold() in valid_file_extentions:
            file_extention = '.png'

        # file name
        if type_of_plot != "":
            n = f'{str(self.path.parent)}/{self.path.stem}-[{type_of_plot}]{file_extention}'
        else:
            n = f'{str(self.path.parent)}/{self.path.stem}{file_extention}'

        self.plot_path = Path(n)

        #if (override == False and not os.path.isfile(n)):
            # save plot to file
        plt.savefig(n, format=file_extention[1:])

        # clear figure/plot for next
        plt.clf()


    def find_bounds(self, fit_function=None):
        """Automatically finds usefull fit bounds and updates them
        in the :code:`fit_function_list` dict.

        :param fit_function:    defines for which fit functions the
                                bounds should be updated (Default
                                value = None), if set to None, type_of_fit
                                will be used

        """
        # check if fit function is not explicitly set for fit()
        if fit_function == None:
            # default fit function for measurement type
            func = self.fit_function_list[self.type_of_fit][0]
        else:
            func = fit_function

        # minima and maxima of x and y data
        #x_min = self.x.min()
        #x_max = self.x.max()
        y_min = self.y[0].min()
        y_max = self.y[0].max()

        # x data where y is max or min
        y_min_i = self.x[self.y[0].argmin()]
        y_max_i = self.x[self.y[0].argmax()]

        # cases for each type of fit
        if func == "gauss":
            # estimate of height of Gaussian
            a = y_max - y_min

            # estimate of middle of Gaussian
            x0 = y_max_i

            # find FWHM first
            fwhm = 2*np.abs(
                self.x[np.abs(self.y - a/2).argmin()] - x0
            )
            # calculating sigma from FWHM
            sigma = fwhm / 2.35

            # scale factor
            s = 0.5
            
            self.fit_function_list['gauss'] = (
                gauss,
                (
                    [a - a*s, x0 - s*x0, sigma - s*sigma],
                    [a + a*s, x0 + s*x0, sigma + s*sigma]
                )
            ) # a, x0, sigma


        elif func == "sine":
            # calculation of amplitude
            a = 0.5 * abs(y_max - y_min)
            # guessing the offset
            c = y_min + a
            # guessing an omega
            omega = np.pi / abs(y_max_i - y_min_i)
            # guessing a phase, works for now, but big values TODO:
            phase = (abs(y_max_i) + abs(y_min_i) / omega) % np.pi

            # scale factor
            s = 0.5

            self.fit_function_list['sine'] = (
                sine, 
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
            # guessing a phase, works for now, but big values TODO:
            phase = (abs(y_max_i) + abs(y_min_i) / omega) % np.pi
            # calculation of slope of linear term (sloppy TODO:)
            b = abs(y_max - y_min) / abs(y_max_i-y_min_i)

            # scale factor
            s = 0.5

            self.fit_function_list['sine_lin'] = (
                sine_lin, 
                (
                    [a - a*s, omega - omega*s, phase - phase*s, c - c*s, - b*s], 
                    [a + a*s, omega + omega*s, phase + phase*s, c + c*s, + b*s]
                )
            ) # a, omega, phase, c, b

            
        elif func == "poly5":
            # TODO:
            pass
        else:
            # reset bounds here useful?!
            pass
            
    def reset_bounds(self, fit_function=None):
        """ Resets the bounds of the measurement type's default fitting
        function if not specified otherwise.

        Reset values are :code:`(-np.inf, np.inf)`.

        :param fit_function:    specifies the fit function for which the
                                bounds should be reset (Default value = None)

        """
        # check if fit function is not explicitly set for fit()
        if fit_function == None:
            # default fit function for measurement type
            func = self.fit_function_list[self.type_of_fit][0]
        else:
            func = fit_function

        self.fit_function_list[func][1] = (-np.inf, np.inf)


    def export_meta(self, make_md=True, make_html=False, theme='github'):
        """ Exports all available information about the measurement into
        a markdown file.

        :param html:    if set to True, an HTML file will be additionally
                        created (Default value = False)
        :param theme:   set the default theme for html export, all
                        available themes can be found in the markdown_themes
                        directory (Default value = 'github')

        """

        # helper vars to build information lists
        header_to_write = {
            'file_path'             :   '[{}]({})'.format(self.path, self.path.name),
            'type_of_measurement'   :   self.type_of_measurement,
            'type_of_fit'           :   self.type_of_fit
        }
        fit_types = {
            'default'   :   ['a', 'x0', 'sigma'],
            'gauss'     :   ['a', 'x0', 'sigma'],
            'sine'      :   ['a', 'omega', 'phase', 'c'],
            'sine_lin'  :   ['a', 'omega', 'phase', 'c', 'b'],
            'poly5'     :   ['a5', 'a4', 'a3', 'a2', 'a1', 'a0']
        }

        # create link to position file (can be in subdirectory of the markdown file)
        if self.pos_file_path != None:
            l_pos = self.pos_file_path.parts
            l_dat = self.path.parts
            p = Path('/'.join([x for x in l_pos if x not in l_dat]))
            header_to_write['pos_file_path'] = '[{}]({})'.format(self.pos_file_path, p)


        # writing all basic information about measurement into var for later use
        basic_information = []
        for k,v in header_to_write.items():
                basic_information.append('- {} : {}'.format(k,v))

        # writing all detector information about measurement into var for later use
        detector_information = []
        for k,v in self.settings.items():
                detector_information.append('- {} : {}'.format(k,v))

        # writing all fit information about measurement into var for later use
        fit_information = []
        for i, popt in enumerate(self.popt):
            for k,v in list(zip(fit_types[self.type_of_fit], popt)):
                # if phase, print in degree's
                if k == 'phase':
                    v = v * 180 / np.pi
                    v = str(v) + '°'
                fit_information.append('- Fit #{} {} : `{}`'.format(i,k,v))

        # try to write boundaries of fit
        boundaries_information = []
        try:
            a = fit_types[self.type_of_fit]
            b = self.fit_function_list[self.type_of_fit][1][0]
            c = self.fit_function_list[self.type_of_fit][1][1]
            for k, v1, v2 in list(zip(a,b,c)):
                boundaries_information.append("- {} : `[{} , {}]`".format(k,v1,v2))
        except Exception as e:
            print(emoji.emojize(":warning:  {}: Error writing boundaries into file: {}".format(self.path,e)))
            boundaries_information = [
                'No information about the boundaries could be presented, because the following exception occured:',
                str(e),
                '',
                'Please report this error by opening a new ticket in Github. Most likely, the function that should detect the boundaries was not defined yet.'
            ]

        # often used paths
        measurement_file_name = self.path.name
        try:
            plot_file_name = self.plot_path.name
        except AttributeError:
            plot_file_name = None

        # minima and maxima of x and y data
        x_min = self.x.min()
        x_max = self.x.max()
        y_min = [y.min() for y in self.y]
        y_max = [y.max() for y in self.y]

        # x data where y is max or min
        y_min_i = [self.x[y.argmin()] for y in self.y]
        y_max_i = [self.x[y.argmax()] for y in self.y]


        try:
            fit_function = self.used_fit_function
        except AttributeError:
            self.fit()
            fit_function = self.used_fit_function

        fit_y_min, fit_y_max, fit_y_min_i, fit_y_max_i = [], [], [], []
        x = np.linspace(self.x.min(), self.x.max(), self.FIT_RESOLUTION)
        for popt in self.popt:
            f = fit_function[0](x, *popt)

            fit_y_min.append(f.min())
            fit_y_max.append(f.max())
            
            x_range = x_max-x_min
            
            fit_y_min_i.append(
                x_min + x_range * f.argmin() / self.FIT_RESOLUTION
            )
            fit_y_max_i.append(
                x_min + x_range * f.argmax() / self.FIT_RESOLUTION
            )
        
        # text to write to file
        t = ['# Metadata for {}'.format(measurement_file_name)]

        # if plot exists, insert it into markdown file
        if plot_file_name:
            t.append('![{}](./{} "{}")'.format(measurement_file_name, plot_file_name, measurement_file_name))
        
        # building the markdown
        t.extend(
            [
                '',
                '## Basic Information',
                'Here is some basic information about the measurement, which was either provided by you, or automatically detected.',
                ''
            ]
        )
        t.extend(basic_information)
        t.extend(
            [
                '',
                '## Detector Information',
                'Here is some basic information about the measurement, which was either provided by you, or automatically detected.',
                ''
            ]
        )
        
        t.extend(detector_information)
        t.extend(
            [
                '',
                '## Extreme Values',
                '',
                '- x_min: `{}`'.format(x_min),
                '- x_max: `{}`'.format(x_max),
                '- y_min: `{}`'.format(y_min),
                '- y_max: `{}`'.format(y_max),
                '',
                'Horizontal axis values where vertical axis is max or min:',
                '',
                '- y_min_i: `{}`'.format(y_min_i),
                '- y_max_i: `{}`'.format(y_max_i),
                '',
                'This gives a contrast of `{}`.'.format(self.contrast(source='data')),
                '',
                '## Fit ({})'.format(self.type_of_fit),
                '',
                '### Fit Extrema',
                '- y_min: `{}`'.format(fit_y_min[0]),
                '- y_max: `{}`'.format(fit_y_max[0]),
                '- y_min_i: `{}`'.format(fit_y_min_i[0]),
                '- y_max_i: `{}`'.format(fit_y_max_i[0]),
                '',
                '### Fit Parameters, Covariance and Contrast',
                '',
                'Parameters:',
                ''
            ]
        )
        t.extend(fit_information)
        covariance_as_string = ["".join(np.array2string(pcov, separator=', ')) for pcov in self.pcov]
        t.extend(
            [
                '',
                'Covariance:',
                '```',
                *covariance_as_string,
                '```',
                ''
            ]
        )
        for i, contrast in enumerate(self.contrast(source='fit')):
            t.extend([f'Contrast for fit #{i}: `{contrast}`'])
        t.extend([
                '',
                '### Fit Boundaries',
                ''
            ]
        )
        t.extend(boundaries_information)

        # write markdown file
        if make_md == True:
            with open(self.path.with_suffix('.md'), 'w') as mdfile: 
                for line in t:
                    mdfile.write('{}\n'.format(line))

        # write html file
        if make_html == True:
            h1 = [
                '<!DOCTYPE html>',
                '<html>',
                '<head>',
                '<meta charset="UTF-8">',
                '<title>{}</title>'.format(measurement_file_name),
                '<style>'
            ]
            h2 = [
                '</style>',
                '</head>',
                '<body>',
                markdown('\n'.join(t), extensions=['fenced_code', 'codehilite']),
                '</body>',
                '</html>'
            ]
            
            with open(self.path.with_suffix('.html'), 'w') as htmlfile:
                # writing html head
                for line in h1:
                    htmlfile.write('{}\n'.format(line))

                # copying the css file
                css_path = Path('./markdown_themes/{}.css'.format(theme))
                with open(css_path, 'r') as cssfile:
                    for line in cssfile:
                        htmlfile.write(line)

                # write actual content of html file and end
                for line in h2:
                    htmlfile.write('{}\n'.format(line))

    def contrast(self, source='fit'):
        """ Calculates the contrast of source as:

        :code:`contrast = (max-min) / (max+min)`

        where :code:`min` and :code:`max` are the minima and maxima of the given data.

        :param source:  defines the source of the data to calculate the contrast from,
                        can be either set to 'fit' or 'data' (Default value = 'fit')

        Returns a list of contrasts.

        .. todo:: When calculation of contrast fails, what should this function return? Now it returns [0].
        """

        _min = list()
        _max = list()

        # calculate min and max of fit
        if source == 'fit':
            try:
                fit_function = self.used_fit_function
            except AttributeError:
                self.fit()
                fit_function = self.used_fit_function

            x = np.linspace(self.x.min(), self.x.max(), self.FIT_RESOLUTION)
            for popt in self.popt:
                f = fit_function[0](x, *popt)
                _min.append(f.min())
                _max.append(f.max())


        # calculate min and max of real data
        elif source == 'data':
            for y in self.y:
                _min.append(y.min())
                _max.append(y.max())

        # TODO: not ideal
        else:
            print(emoji.emojize(":red_circle:  {}: Could not calculate contrast.".format(self.path)))
            _max = _min = [1]
        
        # return list of contrasts
        return [abs((a-b) / (a+b)) for a, b in zip(_min,_max)]



# here you can test the class
if __name__ == "__main__":
    print('Testing the Measurement Class')
    
    m1 = Measurement(Path("./testfiles/polarimeter/2019_02_20_1340_dc2z_scan.dat"))
    m1.fit()
    #m1.plot()
    m1.export_meta(make_html=False, make_md=True)

    #m2 = Measurement(Path("./testfiles/polarimeter/2018-11-23-1545-scan-dc2x.dat"))
    #print(m2.type_of_measurement)
    #m2.fit()
    #m2.plot()
    #print(len(m2.y))
    #print(len(m2.x))
    #print(m2.head)
    #print(m2.data)

    #m.find_bounds()
    #m.fit()
    #m.plot()
    