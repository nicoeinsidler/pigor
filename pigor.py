#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
from os import walk

PROGRAM_NAME = "PIGOR"

f = []
d = []
for (dirpath, dirnames, filenames) in walk("."):
    f.extend(filenames)
    d.extend(dirnames)
    break

print(f)
print(d)

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


# starting main loop
print_header("Welcome to {}.".format(PROGRAM_NAME))
while True:
    cmd = input()
    if cmd == "q":
        break
    elif cmd == "h":
        print_help()
    else:
        pass