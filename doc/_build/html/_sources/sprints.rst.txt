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
    - improvement: use JSON for config file
3. Sprint:
	- feature: auto run command in specified intervals; syntax maybe: time + [cmd] + <ENTER>


Measurement Class
-----------------

1. Sprint
    - ✓ improvement: switching from self.y --> self.y[] and self.y_error --> self.y_error[]
    - ✓ [not tested yet] improvement: plot multiple self.y's
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

.. mermaid::

    graph TD
        subgraph column class
        desc(Column.desc) --> column{column object}
        data(Column.data) --> column{column object}
        end

        column --> dsdata

        subgraph data set object
        dsdesc(DataSet.desc) --> set{data set object}
        dsdata(DataSet.data) --> set
        end

        subgraph fit function class
        parameters(FitFunction.parameters) --> ff
        find_bounds[find_bounds] --> fb
        fb(FitFunction.bounds) --> ff
        end

        ff{fit function class} --> find_fit[find_fit]
        ff --> fit_function
        set --> fdata(fit.data)

        subgraph fit class
        find_fit --> fit
        popt(fit.popt) --> fit
        pcovt(fit.pcov) --> fit
        fit_function(fit.fit_function) --> fit
        ft(fit.type) --> fit
        fdata --> fit
        end

        fit{fit object} --> m
        set --> m{measurement object}

        subgraph measurement class
        m --> plot[plot]
        m --> export[export_meta]
        end

        subgraph legend
        l1{class}
        l2(variable)
        l3[function]
        end


Column Class
------------

Methods:

- :code:`reverse()`: reverse order of data
- :code:`__init__(self, desc, data)`
- :code:`__repr__()`: plots :code:`'<column object 'desc' of lenght len(data)>'` or something like that


Variables:

- :code:`columns.data`: holds the data as numpy array in float64
- :code:`columns.desc`: holds the name of the columns heading as string


Fit Function Class
------------------

Method:

- :code:`fit_function()`
- :code:`find_bounds()`: tries to find the bounds
- :code:`bounds`: holds the bounds to be used when fitting as array of tuples

Variables:

- :code:`parameters`: dictionary holding the names of the parameters and the parameters themselves


Fit Class
---------

Variables:

- :code:`type` with which function the fit should be carried out, string
- :code:`popt`
- :code:`pcov`

Methods:

- :code:`fit()`

Data Set Class
--------------

This object stores data points (lists or Column objects) to form a data set. It must contain at least two data point lists. These lists must have the same number of elements, if not the lists that don't have enough elements will get padded with 0.

Variables:

- :code:`desc`: a description of what the data set describes (optional)
- :code:`data`: data is stored in list; len(list) > 1;