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
        """
        self.directory = directory
        self.file_name = file_name

        self.read_data(self, directory, file_name)


if __name__ == "__main__":
    pass
