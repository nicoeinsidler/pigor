#!/usr/bin/env python3

import os
import ftplib
import pathlib
import tqdm

server = 'www41.world4you.com' 
username = os.environ.get('PIGOR_FTP_USERNAME')
password = os.environ.get('PIGOR_FTP_PASSWORD')

# all file extentions which should be uploaded
file_extentions = [
    '.html',
    '.css',
    '.js',
    '.png',
    '.gif',
    '.jpeg',
    '.svg',
    '.ttf',
    '.woff',
    '.woff2',
    '.eot'
]

# path to the documentation
documentation_path = pathlib.Path('./doc')
html_path = documentation_path.joinpath('_build','html')

def upload_all_files():
    """ Uploads all files that can be found in the doc/ dir to the FTP server. """
    session = ftplib.FTP(server, username, password)
    print('\n'+session.getwelcome()+'\n\n')

    for e in file_extentions:
        all_files = html_path.rglob('*'+e)
        print(f'uploading all {e} files: ')

        for f in tqdm.tqdm(all_files):
            print(f.relative_to(html_path))
            with open(f, 'rb') as file_to_upload:
                path_to_file = f.relative_to(html_path).name
                session.storbinary(path_to_file, file_to_upload)

    session.quit()


if username and password:
    upload_all_files()
else:
    print('Could not find environment variables PIGOR_FTP_USERNAME and PIGOR_FTP_PASSWORD. Exiting the script.')
