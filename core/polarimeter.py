#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from measurement2 import Measurement
import pandas as pd
import numpy as np
import difflib
import re
import matplotlib.pyplot as plt 

try:
    import emoji
except Exception as e:
    print(f'Could not import package emoji. {e}')

class Polarimeter(Measurement):
    """This class extends the Measurement class by adding some polarimeter station specific methods."""



    def __init__(self, file_path, name=None):
        """Fire up :code:`__init__()` of :class:`measurement2.Measurement` and mold data into a :class:`pandas.df`."""
        # create a Measurement object
        super().__init__(file_path, name)

        # create a list for meta infos on polarimeter measurement
        self.settings = {} #: dict containing useful information

        # read the measurement file TODO: handle exceptions
        data = self.read()

        # create a data frame from read file data
        self.make_df(data)

        # if data comes with meta info, make sense of it
        if data[0] != []:
            self.clean_meta(data)

        # detect type of measurement TODO: Exception handling
        self.detect_measurement_type()

        # read position file if degree of polarisation measurement and calculate degree of polarisation
        if self.type_of_measurement == "POL":
            # try to find a position file
            try:
                self.read_pos_file()
                print(emoji.emojize(":round_pushpin:  {}: Position file read: {}".format(self.pos_file_path, self.file_path)))
                self.degree_of_polarisation()
            except Exception as e:
                print(emoji.emojize(":red_circle:  {}: {}".format(self.file_path,e)))

    

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
        """Calculates the degree of polarisation for each position in :code:`pos_data`. 
        
        .. todo:: Refine this function.
        """

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
        if re.search(r"(?i)dc[0-9][xX]", self.file_path.name):
            self.type_of_measurement = "DC"
            self.type_of_fit = "sine_lin"
            self.settings['DC Coil Axis'] = "X"

            # get the number of the DC coil
            match = re.search(r"(?i)dc(\d+)", self.file_path.name)
            if match:
                # write number into self.settings
                self.settings['DC Coil Number'] = match.group(1)

        # else if DC#Z scan
        elif re.search(r"(?i)dc[0-9][zZ]", self.file_path.name):

            self.type_of_measurement = "DC"
            self.type_of_fit = "poly5"
            self.settings['DC Coil Axis'] = "Z"

            # get the number of the DC coil
            match = re.search(r"(?i)dc(\d+)", self.file_path.name)
            if match:
                # write number into self.settings
                self.settings['DC Coil Number'] = match.group(1)

        # else if POS# scan
        elif re.search(r"(?i)pos[0-9]", self.file_path.name):

            self.type_of_measurement = "POS"
            self.type_of_fit = "gauss"

            # get the number of the DC coil
            match = re.search(r"(?i)pos(\d+)", self.file_path.name)
            if match:
                # write number into self.settings
                self.settings['Linear Stage Axis'] = match.group(1)

        # default case
        else:
            # if degree of polarization measurement
            if "pol" in self.file_path.name: 
                self.type_of_measurement = "POL"
                self.type_of_fit = "gauss"
            else:
                self.type_of_measurement = "POS"


        # override type_of_fit if one of the key strings is matched
        for k in self.fit_model_list:
            if k in self.file_path.name: self.type_of_fit = k
        
    def clean_meta(self, data: [list, list, list]):
        """Cleans up meta data and stores it in :code:`self.settings`."""

        meta = [line.split('|') for line in data[0]]

        # write information from head into settings
        #self.settings = {}
        try:
            for line in meta:
                for i, item in enumerate(line):
                    l = item.split(":")
                    if i != 0:
                        self.settings[l[0]] = l[1]
        except Exception as e:
            self.settings = {}
            print(emoji.emojize(":red_circle:  {}: {}".format(self.file_path, e)))

         # try to find measurement time stamp
        try:
            self.settings['time_stamp'] = datetime.strptime(meta[0][0].split()[-1], '%d/%m/%Y@%H:%M')
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


    def plot(self, column1=(0,1), column2=(1,1), fit=True, override=True, file_extention='.png'):
        """Creates a plot for the data. If fit is set to False the data fit won't be
        plotted, even if there exists one. Following parameters are possible:

        :param self:            the object itself
        :param column1:         (column, nth element) to choose the data from for x-axis (Default value = (0)
        :param column2:         (column, nth element) to choose the data from for y-axis (Default value = (1)
        :param fit:             if set to False plotting of the fit will be supressed (Default value = True)
        :param type_of_plot:    string to specify a certain plot type, which will be used
                                in the file name as well as in the plot title (Default value = '')
        :param override:        determines if plot image should be recreated if it already exists (Default value = True)

        """

        if self.type_of_measurement == 'POL':
            data = self.dopd
        else:
            data = self.data.loc[:, ['I Scan (mA)', 'Detector (cnts)']]

            # -----------------------> error muss bei plotten berechnet werden mit lambda und sonst muss viel ausgetauscht weerden, columns: data.loc[data.columns[1,...]]
        
        # create label
        if 'time_stamp' in self.settings:
            title = self.file_path.name + '\n' + self.settings['time_stamp'].strftime("%Y-%m-%d %H:%M")
        else:
            title = self.file_path.name + "\n"

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


if __name__ == "__main__":
    m = Polarimeter('../testfiles/polarimeter/2018-11-23-1545-scan-dc2x.dat', 'test polarimeter')
    m.plot()
    #print(m.data)
    #m.detect_measurement_type()
    #print(m.settings)

    dop = Polarimeter('../testfiles/polarimeter/2018-11-22-1125-degree-of-polarisation.dat')
    dop.degree_of_polarisation()
    dop.plot()

