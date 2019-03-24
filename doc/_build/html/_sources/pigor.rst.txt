PIGOR
=====

What PIGOR does
---------------

PIGOR ('Python IGOR' = PIGOR) aims to help physicists on the NEPTUN beamline to quickly extract the needed information when measuring and configuring or preparing an experiment. It will go through all files in its root folder and will continue to **look for files in all subdirectories recursively** as well. It will then **auto detect** [#f1]_ **the type of measurement** and guess what the user wants to know. After analysis of all files, **additional files will show up alongside the original measurement files**:

- .png file: plot of the data
- .md file: usefull information gathered about the measurement in plain text as markdown
- .html file: same content as the markdown file, but nicely viewable in a modern browser

.. [#f1] This will only work if the correct naming convention is used.

PIGORs inner workings
---------------------

.. automodule:: pigor
    :members: