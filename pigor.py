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

    :param text: text to be displayed as header

    """
    print("\n" + "=" * len(text))
    print(text)
    print("=" * len(text) + "\n")

    # print quick help
    print_help(display="quick")

def print_help(display="all"):
    """Prints a help menu on the screen for the user.

    :param display: specify the lenght of the help menu, options are 'all' or 'quick' (Default value = "all")

    """
    cmd_dict = {
        'h' :   "displays a help menu",
        'q' :   "quit {}".format(PROGRAM_NAME)
        'r' :   "removes all generated files"
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
    return [Path(path) for path in glob.glob('testfiles/**/*.dat', recursive=True)]


def analyse_files(filepaths):
    """Analyses all given files in list.

    :param filepaths:   list of files to analyse with
                        their relative dir path added

    """
    # m = []
    # with mp.Pool() as pool:
    #     m = pool.map(measurement.Measurement, filepaths)
    #     pool.map(measurement.Measurement.fit, m)
    #     pool.map(measurement.Measurement.plot, m)

    # with mp.Pool() as pool:
    #      pool.map(measurement.Measurement.export_meta, m)

    
    for f in filepaths:
        m = measurement.Measurement(f)
        m.fit()
        m.plot()
        m.export_meta(html=True)


def remove_generated_files(files='all'):
    """Removes the generated png, html and md files.
    
    :param files:   list of Path objects to files that should be removed; if set to 'all' it will delete all generated files (Default value = 'all')
    """
    if files == 'all':
        files = find_all_files()
    

    # TODO: case when files is not a list of Paths
    try:
        for f in files:
            f.with_suffix('.png').unlink()
            f.with_suffix('.md').unlink()
            f.with_suffix('.html').unlink()
    except Exception as e:
        print(e)
        raise NotImplementedError
    


def main():
    """Main Loop"""
    # starting main loop
    print_header("Welcome to {}.".format(PROGRAM_NAME))
    while True:
        
        print("To proceed, please press any key.")
        cmd = input()
        if cmd == "q":
            break
        elif cmd == "h":
            print_help()
        elif cmd == 'r':
            remove_generated_files()
        else:
            all_files = find_all_files()
            print(
                "Found {} dat files to analyze. \nProceeding with analysis...".format(len(all_files))
            )
            analyse_files(all_files)
        
if __name__ == '__main__':
    mp.freeze_support()
    main()