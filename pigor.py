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

# functions that the user can utilize
USER_FUNCTIONS = dict()


def show_user(func):
    """Register a function to be displayed to the user as an option"""

    try:
        cmd = re.search('\[(.+?)\]', func.__doc__).group(1)
    except AttributeError as e:
        print(e)

    USER_FUNCTIONS[func.__name__] = (cmd, func)
    return func

def print_header(text):
    """This function prints a beautiful header followed by one empty line.

    :param text: text to be displayed as header

    """
    print("\n" + "=" * len(text))
    print(text)
    print("=" * len(text) + "\n")

    # print quick help
    print_help(display="all")

@show_user
def print_help(display="all"):
    """Prints a help menu on the screen for the user. This function can be used by the command [h].

    :param display: specify the lenght of the help menu, options are 'all' or 'quick' (Default value = "all")

    """
    # print a list of all available commands
    if display == 'all':
        for k,v in USER_FUNCTIONS.items():
            print(f'{v[0]} ... {k}')
        print(f'q ... quit {PROGRAM_NAME}\n')
    # show only the function that should be displayed, but this time with a docstring
    else:
        try:
            f = USER_FUNCTIONS[display]
            print(f'{display}: \n\n {f[1].__doc__}\n\n')
        except Exception as e:
            print(e)
            raise ValueError


def find_all_files():
    """Finds all dat files recursively in all subdirectories ignoring hidden directories
    and Python specific ones.
    
    Returns a list of filepaths.


    """
    return [Path(path) for path in glob.glob('testfiles/**/*.dat', recursive=True)]

@show_user
def analyse_files(filepaths='all'):
    """Analyses all given files in list. This function can be used by the command [a].

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

    # for p in filepaths:
    #     m = measurement.Measurement(p)
    #     m.plot()
    #     m.export_meta(html=True)
    
    if filepaths == 'all':
        filepaths = find_all_files()


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
        print("Please type a command you want to perform and press <ENTER>.")
        cmd = input()
        if cmd == "q":
            break
        elif cmd in [i[0] for i in list(USER_FUNCTIONS.values())]:
            for v in USER_FUNCTIONS.values():
                if v[0] == cmd:
                    f = v[1]
            f()
        else:
            print('The command you typed does not exist. Press h + <ENTER> for help.')
        
if __name__ == '__main__':
    mp.freeze_support()
    main()