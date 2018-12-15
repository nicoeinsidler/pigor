#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt

class Measurement:
    """
    This class provides an easy way to read, analyse and plot data from 
    text files.
    """
    def __init__(self, directory, file_name):
        """
        The Measurement class provides an easy and quick way to read, 
        analyse and plot data from text files. When creating a new instance,
        the following parameters have to be provided:

            :param self: the object itself
            :param directory: the directory of the file to read data from
            :param file_name: the name of the file to read from (containing
                              also its file extention)

        Returns nothing.
        """
        self.directory = directory
        self.file_name = file_name

        try:
            self.read_data(directory, file_name)
        except IOError as e20:
            print(e20)
        except Exception as e:
            print(e)
        
        

    def read_data(self, directory, file_name):
        """
        Reads data from file and stores it in the object.

            :param self: the object itself
            :param directory: the directory of the file to read data from
            :param file_name: the name of the file to read from (containing
                              also its file extention)
        
        Returns nothing if successfull, but rasies exception if not.
        """

        self.raw = [line.rstrip('\n') for line in open(directory + file_name)]
        





if __name__ == "__main__":
    msrmt = Measurement("./testfiles/","2018-12-11-1000-dc1com.dat")
