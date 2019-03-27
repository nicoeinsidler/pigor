Sprint Planning
===============

This site gives a quick overview what will come next. Each sprint should take about 1 week to finish.

PIGOR
-----

1. Sprint
    - ✓ feature: remove all generated files (html, md, png)
    - ✓ feature: introducing a config file (PIGOR start directory, ...)
    - ✓ improvement: auto create config file if not present 
    - ✓ improvement: auto register all functions for help menu (decorators)
2. Sprint
    - feature: remove last generated files (html, md, png)
    - feature: remove all html/md or png files
3. Sprint: not yet planned


Measurement Class
-----------------

1. Sprint
    - improvement: switching from self.y --> self.y[] and self.y_error --> self.y_error[]
    - improvement: plot multiple self.y's
    - feature: auto detect interferometer measurements
2. Sprint
    - feature: remove all associated files from file system, except the measurement file itself
    - ✓ improvement: auto register all available fit functions via decorators
    - improvement: adding __repr__
3. Sprint: finish branch :code:`feature/interferometer`
    - fixing / understanding inheritance of instance variables (see python test file in branch)
    - creating subclasses from Measurement:
        - Interferometer: adding custom maps to COLUMN_MAPS and overriding clean_data() and detect_measurement()
        - Polarimeter: adding custom maps to COLUMN_MAPS and overriding clean_data() and detect_measurement()
4. Sprint: not planned yet


Ideas
-----

Building Measurement from ground up with custom objects like:

- data column: has data and a head, knows its name etc.; functions can easily be applied to it
- fit object: used for fitting and finding bounds; each instance can have its own bounds
- data set: these objects can be plotted by Measurement, so Measurement will try to create one of those objects; they consists of:
    - data columns objects
    - fit objects