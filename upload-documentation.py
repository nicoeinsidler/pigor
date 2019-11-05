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

def upload(session, file_to_upload, root_path) -> bool:
    """ Uploads a file via FTP.
    
    :param session: FTP session
    :type session: ftplib.FTP
    :param file_to_upload: file that you want to upload
    :type file_to_upload: pathlib.Path
    :param root_path:   defines the root path on the client side
                        all uploaded files will be relative to the
                        root_path on the client side, example:
                        /dir1/dir2/file2upload.txt and the root path
                        is /dir1/ then file2upload.txt will be
                        uploaded into dir2 on the FTP server
    :type root_path: pathlib.Path
    :return: success or no success, True if error, False if successfull
    :rtype: bool
    """
    # check if file exists
    if not file_to_upload.exists():
        raise FileNotFoundError
    
    # save current location on server
    session_path = session.pwd()

    # get the parts of the file path and separate the file name
    parts = list(file_to_upload.relative_to(root_path).parts)
    fname = parts[-1]
    parts.pop()

    # go into right directory
    for part in parts:
        # if directory not already present, create one
        if not part in session.nlst():
            session.mkd(part)
        # change into directory
        session.cwd(part)

    with open(file_to_upload, 'rb') as f:
        session.storbinary('STOR ' + fname, f)

    # check if file was written to server
    if fname in session.nlst():
        failure = False
    else:
        failure = True

    # restore location on server
    session.cwd(session_path)

    return failure

def upload_all_files():
    """ Uploads all files that can be found in the doc/ dir to the FTP server. """
    session = ftplib.FTP(server, username, password)
    print('\n'+session.getwelcome()+'\n\n')
    #session.set_debuglevel(2)

    for e in file_extentions:
        all_files = html_path.rglob('*'+e)
        print(f'uploading all {e} files: ')

        for f in tqdm.tqdm(all_files):
            upload(session, f, html_path)

    session.quit()


if username and password:
    upload_all_files()
else:
    print('Could not find environment variables PIGOR_FTP_USERNAME and PIGOR_FTP_PASSWORD. Exiting the script.')
