#!/usr/bin/env python3

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

try:
    import emoji
except Exception as e:
    print("Could not import package emoji. {}".format(e))

class Measurement:
    """This class provides an easy way to read, analyse and plot data from
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
        self.pos_file_path = None

        self.settings = {}

        
        # change type of fit
        self.type_of_fit = type_of_fit

        # list of all available fitting functions with their default bounds
        self.fit_function_list = {
            'default'   :   (self.gauss, (-np.inf, np.inf)), # a, x0, sigma
            'gauss'     :   (self.gauss, (-np.inf, np.inf)), # a, x0, sigma
            'sine'      :   (self.sine, (-np.inf, np.inf)), #  a, omega, phase, c
            'sine_lin'  :   (self.sine_lin, (-np.inf, np.inf)), # a, omega, phase, c, b
            'poly5'     :   (self.poly5, (-np.inf,np.inf)) # a5, a4, a3, a2, a1, a0
        }

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
            self.select_columns()
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

        :param self: object itself
        :param type_of_measurement: default":   new type of measurement
        
        Returns the current type of measurement.

        """
        if type_of_measurement != "default":
            self.type_of_measurement = type_of_measurement
        else:
            # this is the default value of measurement type TODO
            self.type_of_measurement = 'POS'

        return self.type_of_measurement
        
    def detect_measurement_type(self):
        """ """
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
        """Reads data from file and stores it in the object.

        :param self: the object itself
        :param directory: the directory of the file to read data from
        :param file_name: the name of the file to read from (containing
                                also its file extention)
        
        Returns nothing if successfull, but raises exception if not.
        :param path: 

        """

        # import the data
        self.raw = [line.rstrip('\n') for line in open(path)]

    def read_pos_file(self):
        """ """
        # TODO::check if len(pos_data) == len(self.y every 4th) for even better matches

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
            print("{}: No position file found.".format(self.path))

        

    def clean_data(self):
        """Splits the raw data into head and data vars."""

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
                    if i != 1:
                        self.settings[l[0]] = l[1]
        except Exception as e:
            self.settings = {}
            print(e)

        
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
                    break

            self.settings['measurement_time'] = int(re.search(r'\d+', self.settings[match]).group())
            self.settings.pop(match)
        except:
            pass
        


    def select_columns(self, column1=(0,1), column2=(1,1)):
        """

        :param column1:  (Default value = (0)
        :param 1): 
        :param column2:  (Default value = (1)

        """
        self.x = self.data[::column1[1],column1[0]]
        self.y = self.data[::column2[1],column2[0]]

        self.y_error = np.sqrt(self.y)


    def degree_of_polarisation(self):
        """ """

        # select default columns
        self.select_columns()

        # helper vars for raw data
        raw_x = self.x
        raw_y = self.y


        if len(self.pos_data) == len(raw_x):
            # set x axis values from pos file
            self.x = self.pos_data[::4]
        elif len(self.pos_data) > len(raw_x):
            print('Warning: Position file lenght and data file lenght are not equal. Maybe wrong position file?')
            # set x axis values from pos file
            self.x = self.pos_data[::4][0:len(raw_x)//4]
        else:
            print('Could not use position file: Wrong position file!\nContinuing with arbitrary positions: 0 to 1 in {} steps.'.format(len(raw_x)//4))
            self.x = np.linspace(0, 1, len(raw_x)//4) # worst case


        # calculation of degree of polarization and its error
        #self.y = [np.sqrt(((raw_y[i+2] - raw_y[i+3]) * (raw_y[i+2] - raw_y[i+1]))/(raw_y[i+2]*raw_y[i] - raw_y[i+3]*raw_y[i+1])) for i in range(0, len(raw_y)-len(raw_y) % 4, 4)]
        

        # lenght of input data that will be used
        data_lenght = len(raw_y) - len(raw_y)%4

        # allocate arrays to fill later (faster when using numpy)
        self.y = np.zeros(data_lenght//4)
        self.y_error = np.zeros(data_lenght//4)

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
            self.y[i//4] = np.sqrt(
                    np.abs((f1*f2)/(c*d-a*b))
                )

            # calculation of degree of polarisation error
            self.y_error[i//4] = 0.5 * np.sqrt(
                        np.abs((p1*a + p2*c + p3*b + p4*d) / p0)
                )
            

    def fit(self, fit_function=None):
        """

        :param fit_function:  (Default value = None)

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

        # make a curve fit and save values
        self.popt, self.pcov = curve_fit(func[0], self.x, self.y, bounds=func[1], sigma=self.y_error, absolute_sigma=True)

        

    def plot(self, column1=(0,1), column2=(1,1), fit=True, type_of_plot='', override=True):
        """Creates a plot for the data. If fit is set to False the data fit won't be
        plotted, even if there exists one. Following parameters are possible:

        :param self: the object itself
        :param column1: 0,1):   (column, nth element) to choose the data from for x-axis (Default value = (0)
        :param column2: 1,1):   (column, nth element) to choose the data from for y-axis (Default value = (1)
        :param fit: True:        if set to False plotting of the fit will be supressed (Default value = True)
        :param type_of_plot: string to specify a certain plot type, which will be used
                                    in the file name as well as in the plot title (Default value = '')
        :param override: True:   determines if plot image should be recreated if it
                                    already exists (Default value = True)
        :param 1): 

        """
        
        # create label
        if 'time_stamp' in self.settings:
            title = self.path.name + '\n' + type_of_plot + '\n' + self.settings['time_stamp'].strftime("%Y-%m-%d %H:%M")
        else:
            title = self.path.name + "\n" + type_of_plot

        # plot title
        plt.title(title)

        # axes labels
        if self.type_of_measurement == 'POL':
            plt.xlabel('Position (steps)')
            plt.ylabel('Degree of Polarisation')
        else:
            plt.xlabel(self.desc[column1[0]])
            plt.ylabel(self.desc[column2[0]])

        # plot
        plt.errorbar(self.x, self.y, yerr = self.y_error, label='data (Δt={}s)'.format(self.settings['measurement_time']))

        # plot fit if exists
        if fit == True:
            try:
                fit_function = self.used_fit_function
            except AttributeError:
                self.fit()
                fit_function = self.used_fit_function
            x = np.linspace(self.x.min(), self.x.max(), self.FIT_RESOLUTION)
            plt.plot(x, fit_function[0](x, *self.popt), '-', label='fit')

        # plot legend
        plt.legend()

        # file name
        if type_of_plot != "":
            n = str(self.path.parent) + "/" + self.path.stem + "[" + type_of_plot + "].png"
        else:
            n = str(self.path.parent) + "/" + self.path.stem + ".png"

        self.plot_path = Path(n)

        #if (override == False and not os.path.isfile(n)):
            # save plot to file
        plt.savefig(n)

        # clear figure/plot for next
        plt.clf()

    def gauss(self, x, a, x0, sigma):
        """Gaussian function, used for fitting data.

        :param x: parameter
        :param a: amplitude
        :param x0: maximum
        :param sigma: width

        """
        return a*np.exp(-(x-x0)**2/(2*sigma**2))

    def sine_lin(self, x, a, omega, phase, c, b):
        """Sine function with linear term added for fitting data.

        :param self: param x:       parameter
        :param a: amplitude
        :param omega: frequency
        :param phase: phase
        :param c: offset
        :param b: slope
        :param x: 

        """
        return a*np.sin(x*omega + phase) + b*x + c

    def poly5(self, x, a5, a4, a3, a2, a1, a0): # should be implemented as generalization of nth degree
        """Polynom 5th degree for fitting.

        :param x: parameter
        :param a5: coeff
        :param a4: coeff
        :param a3: coeff
        :param a2: coeff
        :param a1: coeff
        :param a0: coeff
        :returns: function -- polynomial 5th degree

        """
        return (((((a5*x + a4)*x + a3)*x + a2)*x + a1)*x + a0)

    def sine(self, x, a, omega, phase, c):
        """Sine function for fitting data.

        :param self: param x:       parameter
        :param a: amplitude
        :param omega: frequency
        :param phase: phase
        :param c: offset
        :param x: 

        """
        return a*np.sin(x*omega + phase) + c

    def find_bounds(self, fit_function=None):
        """

        :param fit_function:  (Default value = None)

        """
        # check if fit function is not explicitly set for fit()
        if fit_function == None:
            # default fit function for measurement type
            func = self.type_of_fit
        else:
            func = fit_function

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
                self.gauss,
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
            # reset bounds here useful?!
            pass
            
    def reset_bounds(self, fit_function=None):
        """

        :param fit_function:  (Default value = None)

        """
        # check if fit function is not explicitly set for fit()
        if fit_function == None:
            # default fit function for measurement type
            func = self.type_of_fit
        else:
            func = fit_function

        self.fit_function_list[func][1] = (-np.inf, np.inf)


    def export_meta(self, html=False, theme='github'):
        """

        :param html:  (Default value = False)
        :param theme:  (Default value = 'github')

        """

        header_to_write = {
            'file_path'             :   '[{}]({})'.format(self.path, self.path.name),
            'type_of_measurement'   :   self.type_of_measurement,
            'type_of_fit'           :   self.type_of_fit
        }
        if self.pos_file_path != None:
            l_pos = self.pos_file_path.parts
            l_dat = self.path.parts
            p = Path('/'.join([x for x in l_pos if x not in l_dat]))
            header_to_write['pos_file_path'] = '[{}]({})'.format(self.pos_file_path, p)

        fit_types = {
            'default'   :   ['a', 'x0', 'sigma'],
            'gauss'     :   ['a', 'x0', 'sigma'],
            'sine'      :   ['a', 'omega', 'phase', 'c'],
            'sine_lin'  :   ['a', 'omega', 'phase', 'c', 'b'],
            'poly5'     :   ['a5', 'a4', 'a3', 'a2', 'a1', 'a0']
        }

        # writing all basic information about measurement into var for later use
        basic_information = []
        for k,v in header_to_write.items():
                basic_information.append('- {} : {}'.format(k,v))

        detector_information = []
        for k,v in self.settings.items():
                detector_information.append('- {} : {}'.format(k,v))

        fit_information = []
        for k,v in list(zip(fit_types[self.type_of_fit],self.popt)):
                fit_information.append('- {} : `{}`'.format(k,v))

        boundaries_information = []
        try:
            a = fit_types[self.type_of_fit]
            b = self.fit_function_list[self.type_of_fit][1][0]
            c = self.fit_function_list[self.type_of_fit][1][1]
            for k, v1, v2 in list(zip(a,b,c)):
                boundaries_information.append("- {} : `[{} , {}]`".format(k,v1,v2))
        except Exception as e:
            boundaries_information = [
                'No information about the boundaries could be presented, because the following exception occured:',
                str(e),
                '',
                'Please report this error by opening a new ticket in Bitbucket. Most likely, the function that should detect the boundaries was not defined yet.'
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
        y_min = self.y.min()
        y_max = self.y.max()

        # x data where y is max or min
        y_min_i = self.x[self.y.argmin()]
        y_max_i = self.x[self.y.argmax()]
        
        # text to write to file
        t = ['# Metadata for {}'.format(measurement_file_name)]

        # if plot exists, insert it into markdown file
        if plot_file_name:
            t.append('![{}](./{} "{}")'.format(measurement_file_name, plot_file_name, measurement_file_name))
        
        t.extend(
            [
                '## Basic Information',
                'Here is some basic information about the measurement, which was either provided by you, or automatically detected.',
                ''
            ]
        )
        t.extend(basic_information)
        t.extend(
            [
                '## Detector Information',
                'Here is some basic information about the measurement, which was either provided by you, or automatically detected.',
                ''
            ]
        )
        
        t.extend(detector_information)
        t.extend(
            [
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
                '### Fit Parameters, Covariance and Contrast',
                'Parameters:',
                ''
            ]
        )
        t.extend(fit_information)
        t.extend(
            [
                '',
                'Covariance:',
                '```\n{}\n```'.format(np.array2string(self.pcov, separator=', \n')),
                '',
                'Contrast: `{}`'.format(self.contrast(source='fit')),
                '### Fit Boundaries',
                ''
            ]
        )
        t.extend(boundaries_information)

        # write markdown file
        with open(self.path.with_suffix('.md'), 'w') as mdfile: 
            for line in t:
                mdfile.write('{}\n'.format(line))

        # write html file
        if html == True:
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
                markdown('\n'.join(t)),
                '</body></html>'
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
        """

        :param source:  (Default value = 'fit')

        """
        # calculate contrast of fit
        if source == 'fit':
            try:
                fit_function = self.used_fit_function
            except AttributeError:
                self.fit()
                fit_function = self.used_fit_function

            x = np.linspace(self.x.min(), self.x.max(), self.FIT_RESOLUTION)
            f = fit_function[0](x, *self.popt)
            min = f.min()
            max = f.max()

        # calculate contrast of real data
        elif source == 'data':
            min = self.y.min()
            max = self.y.max()

        # TODO: not ideal
        else:
            print(emoji.emojize(":red_circle:  {}: Could not calculate contrast.".format(self.path)))
            max = min = 1
        
        return (max-min) / (max+min)

    

# here you can test the class
if __name__ == "__main__":
    print('Testing the Measurement Class')
    
    m1 = Measurement(Path("./testfiles/subdirectory_test/2018-11-22-1125-degree-of-polarisation.dat"))
    m1.fit()
    m1.plot()

    #m2 = Measurement(Path("./testfiles/2018-11-23-1545-scan-dc2x.dat"))
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
    