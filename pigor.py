#!/usr/bin/env python3

import re
import os
import json
import numpy as np
import multiprocessing as mp
import matplotlib.pyplot as plt
import glob
import measurement
import datetime
from pathlib import Path
from markdown import markdown

# name of the program
PROGRAM_NAME = "PIGOR v1.1"

# functions that the user can utilize
USER_FUNCTIONS = dict()

# global config dict
configuration = dict()

# global vars for init() default
configuration_fallback = {
    'PIGOR_ROOT'            :   Path(os.path.dirname(os.path.abspath(__file__))),
    'PIGOR_ROOT_RECURSIVE'  :   True,
    'FILE_EXTENTION'        :   '.dat',
    'IMAGE_FORMAT'          :   '.png',
    'CREATE_HTML'           :   True,
    'CREATE_MD'             :   True
}


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

def bool2yn(b):
    """Converts a boolean to yes or no with the mapping: y = True, n = False."""
    return 'y' if b else 'n'

def yn2bool(s):
    """Converts yes and no to True and False."""
    return True if s.casefold().startswith('y') else False


@show_user
def init(create_new_config_file=True):
    """This function will read the config file and initialize some variables
    accordingly. This function can be used by the command [i].

    Available options:

    - root directory where PIGOR will start to look for measurement files
    - Should PIGOR look for files to analyse recursively?
    - Which file extention do the measurement files posess?
    - What plot output format should PIGOR use?
    - Should PIGOR automatically create an html file?
    - Should PIGOR automatically create a md file?
    
    .. note:: If no config file can be found, it will create one.
    
    """
    
    # make configuration editable
    global configuration


    # try to read the configuration
    try:
        with open('pigor.config', 'r', encoding='utf-8') as f:
            c = json.load(f)
            # make it a path object
            c['PIGOR_ROOT'] = Path(c['PIGOR_ROOT']).resolve()
    except Exception:
        print('Could not read configuration file. Creating a new one now:\n')
        c = configuration_fallback
        create_new_config_file = True
        

    # questions to aks the user
    questions = {
        'PIGOR_ROOT'            :   (f'Where should {PROGRAM_NAME} start looking for measurement files? [{c["PIGOR_ROOT"]}]', 'path'),
        'PIGOR_ROOT_RECURSIVE'  :   (f'Should {PROGRAM_NAME} look for files recursively? (y/n) [{bool2yn(c["PIGOR_ROOT_RECURSIVE"])}]', 'bool'),
        'FILE_EXTENTION'        :   (f'Which file extention should {PROGRAM_NAME} look for? (string) [{c["FILE_EXTENTION"]}]', 'file-extention-dat'),
        'IMAGE_FORMAT'          :   (f'What image format should the plots have? (.png,.svg,.eps,.pdf) [{c["IMAGE_FORMAT"]}]', 'file-extention-png'),
        'CREATE_HTML'           :   (f'Should {PROGRAM_NAME} create an HTML file automatically after analysis? (y/n) [{bool2yn(c["CREATE_HTML"])}]', 'bool'),
        'CREATE_MD'             :   (f'Should {PROGRAM_NAME} create a Markdown file automatically after analysis? (y/n) [{bool2yn(c["CREATE_MD"])}]', 'bool')
    }

    for k, q in questions.items():
        if not k in c.keys() or create_new_config_file:
            # ask user a question
            print(q[0])
            user_input = input()
            # if a Path object must be read
            if q[1] == 'path':
                while True:
                    try:
                        if user_input == '':
                            value = None
                            break
                        value = Path(user_input)
                        if value.exists():
                            break
                        else:
                            print('The path you entered does not exist. Please try again.')
                    except Exception:
                        user_input = input('Could not find the path, please input another one:\n')
            
            # if treating booleans
            elif q[1] == 'bool':
                if not user_input == '':
                    value = yn2bool(user_input)
                else:
                    value = None
            
            # if answer is a file extention
            elif q[1].startswith('file-extention'):
                if user_input == '' and q[1] == 'file-extention-png':
                    user_input = '.png'
                elif user_input == '' and q[1] == 'file-extention-dat':
                    user_input = '.dat'
                # adding . to file extention if not given by the user
                value = user_input.casefold() if user_input.startswith('.') else '.' + user_input.casefold()
            else:
                value = user_input

            # renew old configuration value
            if value != None:
                c[k] = value



    # write config to global var
    configuration = c.copy()

    #print(configuration)

    # write configuration into file
    with open('pigor.config', 'w') as f:
        if isinstance(c['PIGOR_ROOT'], Path):
            c['PIGOR_ROOT'] = str(c['PIGOR_ROOT'].resolve())
        json.dump(c, f, ensure_ascii=False)


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
    if configuration['PIGOR_ROOT_RECURSIVE']:
        return sorted(configuration['PIGOR_ROOT'].rglob('*' + configuration['FILE_EXTENTION']))
    else:
        return sorted(configuration['PIGOR_ROOT'].glob('*' + configuration['FILE_EXTENTION']))

@show_user
def analyse_files(filepaths='all'):
    """Analyses all given files in list. This function can be used by the command [a].

    :param filepaths:   list of files to analyse with
                        their relative dir path added

    .. todo:: Change to no override mode. measurement.Measurement.plot(override=False)
    .. todo:: a + today => only analyse files for today
    .. todo:: a + override => override=True

    """
   
    if filepaths == 'all':
        filepaths = find_all_files()
    elif filepaths == 'today':
        pass # TODO: only analyse the files of today

    # analyse all files
    for f in filepaths:
        try:
            m = measurement.Measurement(f)
            m.fit()
            m.plot(file_extention=configuration['IMAGE_FORMAT'])
            m.export_meta(make_html=True)
        except Exception as e:
            print(f'The following exception occured during runtime:\n\n{e}\n\nContinuing operation.')

@show_user
def create_index():
    """Creates an index.html listing all directories and subdirectories and their HTML and Markdown files. This function can be used by the command [j]."""
    
    # theme for the index.html
    theme = 'github'

    # find all measurements
    files = sorted(configuration['PIGOR_ROOT'].rglob('*' + configuration['FILE_EXTENTION']))
    files = [f.relative_to(configuration['PIGOR_ROOT'].parent) for f in files]

    files.sort(key=lambda x: x.name, reverse=True)

    # list all measurement files, if they have a corresponding html or md file
    l = []
    for f in files:
        buffer = f'- {f.parent}: [{f.stem}]({f.resolve().as_uri()}): '

        m = f.with_suffix('.md').exists()
        h = f.with_suffix('.html').exists()
        p = f.with_suffix(configuration['IMAGE_FORMAT']).exists()

        
        if m:
            buffer += f'[MD]({f.with_suffix(".md").resolve().as_uri()})'
        if h:
            buffer += f' | [HTML]({f.with_suffix(".html").resolve().as_uri()})'
        if p:
            buffer += f' | [PLOT]({f.with_suffix(configuration["IMAGE_FORMAT"]).resolve().as_uri()})'

        if m or h:
            l.append(buffer)

    if l:
        # write header of index.html
        t = [
            f'# {PROGRAM_NAME} Index File',
            '',
            'Here is a handy list of all the files that have been analysed so far:',
            ''
        ]
        t.extend(l)

        # write html template
        h1 = [
            '<!DOCTYPE html>',
            '<html>',
            '<head>',
            '<meta charset="UTF-8">',
            f'<title>{PROGRAM_NAME} Index File</title>',
            '<style>'
        ]
        h2 = [
            '</style>',
            '</head>',
            '<body>',
            markdown('\n'.join(t)),
            '</body>',
            '</html>'
        ]

        index_file_path = configuration['PIGOR_ROOT'].joinpath('index_pigor.html')
        with open(index_file_path, 'w') as htmlfile:
            # writing html head
            for line in h1:
                htmlfile.write(f'{line}\n')

            # copying the css file
            css_path = Path('./markdown_themes/{}.css'.format(theme))
            with open(css_path, 'r') as cssfile:
                for line in cssfile:
                    htmlfile.write(line)

            # write actual content of html file and end
            for line in h2:
                htmlfile.write(f'{line}\n')

        print(f'Wrote index file at {index_file_path}')


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
            f.with_suffix(configuration['IMAGE_FORMAT']).unlink()
            f.with_suffix('.md').unlink()
            f.with_suffix('.html').unlink()
    except Exception as e:
        print(e)
        #raise NotImplementedError
    
@show_user
def print_root():
    """Prints the root for PIGOR, e.g. where it will look for files to analyse. This function
    can be used by the command [x].
    """
    print(f"{PROGRAM_NAME} will look for measurement files in {configuration['PIGOR_ROOT'].resolve()}.\n")


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
