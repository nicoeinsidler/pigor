#!/usr/bin/env python3

import re
import os
import numpy as np
import multiprocessing as mp
import matplotlib.pyplot as plt
import glob
import measurement
import datetime
from pathlib import Path

# name of the program
PROGRAM_NAME = "PIGOR"

# functions that the user can utilize
USER_FUNCTIONS = dict()

# global vars for init() default
PIGOR_ROOT              = Path(os.path.dirname(os.path.abspath(__file__)))
PIGOR_ROOT_RECURSIVE    = True
FILE_EXTENTION          = '.dat'
CREATE_HTML             = True
CREATE_MD               = True

# decorator for registering functions
def show_user(func):
    """Register a function to be displayed to the user as an option"""

    global USER_FUNCTIONS

    try:
        key = re.search(r'\[(.+?)\]', func.__doc__).group(1)
    except AttributeError as e:
        key = func.__name__
        print(e)

    USER_FUNCTIONS[key] = func
    return func

@show_user
def init(create_new_config_file=True):
    """This function will read the config file and initialize some variables
    accordingly. This function can be used by the command [i].

    Available options:

    - root directory where PIGOR will start to look for measurement files
    - Should PIGOR look for files to analyse recursively?
    - Which file extention do the measurement files posess?
    - Should PIGOR automatically create an html file?
    - Should PIGOR automatically create a md file?
    
    .. note:: If no config file can be found, it will create one.

    .. todo:: Creating a loop that goes through each question.
    
    """
    
    global PIGOR_ROOT
    global PIGOR_ROOT_RECURSIVE
    global FILE_EXTENTION
    global CREATE_HTML
    global CREATE_MD

    configuration = False
    # try to read the configuration
    try:
        with open('pigor.config', 'r') as f:
            configuration = dict()
            for line in f.readlines():
                if not line.startswith('#'):
                    k, v = line.split('=')
                    configuration[k.strip()] = v.strip()
    except Exception:
        print('Could not read configuration file. Creating a new one now:\n')

    # try to read the values in configuration
    if configuration:
        for k, v in configuration.items():
            if k == 'PIGOR_ROOT':
                try:
                    PIGOR_ROOT = Path(v)
                except:
                    pass
            elif k == 'PIGOR_ROOT_RECURSIVE':
                if v == 'True':
                    PIGOR_ROOT_RECURSIVE = True
                elif v == 'False':
                    PIGOR_ROOT_RECURSIVE = False
            elif k == 'CREATE_HTML':
                if v == 'True':
                    CREATE_HTML = True
                elif v == 'False':
                    CREATE_HTML = False
            elif k == 'CREATE_MD':
                if v == 'True':
                    CREATE_MD = True
                elif v == 'False':
                    CREATE_MD = False
            elif k == 'FILE_EXTENTION':
                FILE_EXTENTION = v
        
    # ask for root directory TODO: make this if statement more compact
    if not configuration or not 'PIGOR_ROOT' in configuration.keys() or create_new_config_file:
        while True:
            print(f'Where should {PROGRAM_NAME} start looking for measurement files? [{PIGOR_ROOT}]')
            user_input = input()
            try:
                PIGOR_ROOT = Path(user_input)
                break
            except Exception:
                print('The path you provided could not be read, please try again.')

    # ask if recursion when searching for files
    if not configuration or not 'PIGOR_ROOT_RECURSIVE' in configuration.keys() or create_new_config_file:
        if PIGOR_ROOT_RECURSIVE:
            default = 'y'
        else:
            default = 'n'
        print(f'Should {PROGRAM_NAME} look for files in {PIGOR_ROOT} recursively? (y/n) [{default}]')
        user_input = input()
        if user_input == 'n':
            PIGOR_ROOT_RECURSIVE = False
        else:
            PIGOR_ROOT_RECURSIVE = True

    # ask for file extention to look for
    if not configuration or not 'FILE_EXTENTION' in configuration.keys() or create_new_config_file:
        print(f'Which file extention should {PROGRAM_NAME} look for? (string) [{FILE_EXTENTION}]')
        user_input = input()
        if user_input == '':
            user_input = FILE_EXTENTION
        if not user_input.startswith('.'):
            FILE_EXTENTION = '.' + user_input
        else:
            FILE_EXTENTION = user_input

    # ask if html files should be created
    if not configuration or not 'CREATE_HTML' in configuration.keys() or create_new_config_file:
        if CREATE_HTML:
            default = 'y'
        else:
            default = 'n'
        print(f'Should {PROGRAM_NAME} create an HTML file automatically after analysis? (y/n) [{default}]')
        user_input = input()
        if user_input == 'n':
            CREATE_HTML = False
        else:
            CREATE_HTML = True

    # ask if md files should be created
    if not configuration or not 'CREATE_MD' in configuration.keys() or create_new_config_file:
        if CREATE_MD:
            default = 'y'
        else:
            default = 'n'
        print(f'Should {PROGRAM_NAME} create a Markdown file automatically after analysis? (y/n) [{default}]')
        user_input = input()
        if user_input == 'n':
            CREATE_MD = False
        else:
            CREATE_MD = True

    t = [
            '# PIGOR Configuration File',
            f'# automatically created {datetime.datetime.now().date()}',
            f'PIGOR_ROOT = {PIGOR_ROOT}',
            f'PIGOR_ROOT_RECURSIVE = {PIGOR_ROOT_RECURSIVE}',
            f'FILE_EXTENTION = {FILE_EXTENTION}',
            f'CREATE_HTML = {CREATE_HTML}',
            f'CREATE_MD = {CREATE_MD}'
    ]
    with open('pigor.config', 'w') as f:
        for line in t:
            f.write(line + '\n')

def print_header(text):
    """This function prints a beautiful header followed by one empty line.

    :param text: text to be displayed as header

    """
    print("\n" + "=" * len(text))
    print(text)
    print("=" * len(text) + "\n")

@show_user
def print_help(display="all"):
    """Prints a help menu on the screen for the user. This function can be used by the command [h].

    :param display: specify the lenght of the help menu, options are 'all' or 'quick' (Default value = "all")

    """
    # print a list of all available commands
    if display == 'all':
        for k,v in USER_FUNCTIONS.items():
            print(f'{k} ... {v.__name__}')
        print(f'q ... quit {PROGRAM_NAME}\n')

    # show only the function that should be displayed, but this time with a docstring
    else:
        try:
            f = USER_FUNCTIONS[display[0]]
            print(f'{display[0]}: \n\n {f.__doc__}\n\n')
        except Exception:
            print(f'Sorry, but there is not help page for {display[0]} available.\n')


def find_all_files():
    """Finds all dat files recursively in all subdirectories ignoring hidden directories
    and Python specific ones.
    
    Returns a list of filepaths.


    """
    if PIGOR_ROOT_RECURSIVE:
        return sorted(PIGOR_ROOT.rglob('*'+FILE_EXTENTION))
    else:
        return sorted(PIGOR_ROOT.glob('*'+FILE_EXTENTION))

@show_user
def analyse_files(filepaths='all'):
    """Analyses all given files in list. This function can be used by the command [a].

    :param filepaths:   list of files to analyse with
                        their relative dir path added

    .. todo:: Change to no override mode. measurement.Measurement.plot(override=False)
    .. todo:: a + today => only analyse files for today
    .. todo:: a + override => override=True

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
    elif filepaths == 'today':
        pass # TODO: only analyse the files of today

    for f in filepaths:
        try:
            m = measurement.Measurement(f)
            m.fit()
            m.plot()
            m.export_meta(make_html=True)
        except Exception as e:
            print(f'The following exception occured during runtime:\n\n{e}\n\nContinuing operation.')


@show_user
def remove_generated_files(files='all'):
    """Removes the generated png, html and md files. This function can be used by the command [r].
    
    :param files:   list of Path objects to files that should be removed; if set to 'all' it will delete all generated files (Default value = 'all')

    .. todo:: Cover the case when files are not a list of path, e.g. wrong input given.
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
    
@show_user
def print_root():
    """Prints the root for PIGOR, e.g. where it will look for files to analyse. This function
    can be used by the command [x].
    """
    print(f"{PROGRAM_NAME} will look for measurement files in {PIGOR_ROOT.resolve()}.")


def main():
    """Main Loop"""

    # perform initialization
    init(create_new_config_file=False)

    # starting main loop
    print_header("Welcome to {}.".format(PROGRAM_NAME))
    # print help menu
    print_help(display="all")
    # print where PIGOR will look for files in
    print_root()
    print('If you need more information about a command, just type h + [command] + <ENTER> to get more help. For example: h + a + <ENTER>.\n')

    while True:
        print("Please type a command you want to perform and press <ENTER>.")

        # get the user's input
        user_input = input()
        # split it for additional but optional arguments
        cmd, *args = user_input.split(' ')

        if cmd == "q":
            break
        elif cmd in USER_FUNCTIONS.keys():
            f = USER_FUNCTIONS[cmd]
            if args:
                f(args)
            else:
                f()
        else:
            print('The command you typed does not exist. Press h + <ENTER> for help.')
        
if __name__ == '__main__':
    mp.freeze_support()
    main()