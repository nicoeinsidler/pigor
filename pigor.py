#!/usr/bin/env python3

import re
import numpy as np
import multiprocessing as mp
import matplotlib.pyplot as plt
import glob
import measurement
from pathlib import Path

# name of the program
PROGRAM_NAME = "PIGOR"


def print_header(text):
    """This function prints a beautiful header followed by one empty line.

    :param text: 

    """
    print("\n" + "=" * len(text))
    print(text)
    print("=" * len(text) + "\n")

    # print quick help
    print_help(display="quick")

def print_help(display="all"):
    """Prints a help menu on the screen for the user.
    
    display    ... specify the lenght of the help menu, options are 'all' or 'quick'

    :param display:  (Default value = "all")

    """
    cmd_dict = {
        'h' :   "displays a help menu",
        'q' :   "quit {}".format(PROGRAM_NAME)
    }

    if display == "quick":
        print("{:.<4} {}".format("h",cmd_dict['h']))
        print("{:.<4} {}".format("q",cmd_dict['q']))
    else:
        for k,v in cmd_dict.items():
            print("{:.<4} {}".format(k,v))
    print("\n")

def find_all_files():
    """Finds all dat files recursively in all subdirectories ignoring hidden directories
    and Python specific ones.
    
    Returns a list of filepaths.


    """
    return [Path(path) for path in glob.glob('**/*.dat', recursive=True)]


def analyse_files(filepaths):
    """Analyses all given files in list.

    :param filepaths: list of files to analyse with
                                their relative dir path added

    """

    # list holding all measurement objects
    #m = []

    for p in filepaths:
        m = measurement.Measurement(p)
        m.plot()
        m.export_meta(html=True)
        

    # with mp.Pool() as pool:
    #     m = pool.map(measurement.Measurement, filepaths)
    #     pool.map(measurement.Measurement.fit, m)
    #     pool.map(measurement.Measurement.plot, m)
        #pool.map(measurement.Measurement.pcov, m)
        #pool.map(lambda obj: obj.plot(), m)



def main():
    """ Main Loop """
    # starting main loop
    print_header("Welcome to {}.".format(PROGRAM_NAME))
    while True:
        
        print("To proceed, please press any key.")
        cmd = input()
        if cmd == "q":
            break
        elif cmd == "h":
            print_help()
        else:
            all_files = find_all_files()
            print(
                "Found {} dat files to analyze. \nProceeding with analysis...".format(len(all_files))
            )

            analyse_files(all_files)
        
if __name__ == '__main__':
    mp.freeze_support()
    main()