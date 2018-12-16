#!/usr/bin/env python3

import re
import numpy as np
import multiprocessing as mp
import matplotlib.pyplot as plt
from os import walk
import measurement

# name of the program
PROGRAM_NAME = "PIGOR"


def print_header(text):
    """
    This function prints a beautiful header followed by one empty line.
    """
    print("\n" + "=" * len(text))
    print(text)
    print("=" * len(text) + "\n")

    # print quick help
    print_help(display="quick")

def print_help(display="all"):
    """
    Prints a help menu on the screen for the user.

    display    ... specify the lenght of the help menu, options are 'all' or 'quick'

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

def find_all_files(directory="."):
    """
    Finds all dat files recursively in all subdirectories ignoring hidden directories
    and Python specific ones.

        :param directory=".":   directory to start searching from 
    """
    f = []
    d = []
    
    for (dirpath, dirnames, filenames) in walk(directory):
        f.extend(filenames)
        d.extend(dirnames)
        break
    
    # filter all dat files
    f = [a for a in f if re.search(r".dat$", a)]

    # filter directories
    d = [_ for _ in d if not (_.startswith('.') or _.startswith('__'))]

    # check if there are subdirs
    if len(d) > 0:
        for _ in d:
            f.extend(find_all_files(_))

    return f


def analyse_files(files):
    


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
        f = find_all_files()
        print(
            "Found {} dat files to analyze. \nProceeding with analysis...".format(len(f))
        )

        analyse_files(f)

        #with mp.Pool(processes=8) as pool:
         #   pool.starmap(np.dot, zip(a[0:N:2], a[1:N-1:2]))
        