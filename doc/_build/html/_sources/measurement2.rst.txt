Measurement Class 2.0
=====================

Due to some design flaws in the existsing :class:`measurement.Measurement` class, it will be rewritten from ground up using already existsing libraries. This undertaking will lead to a cleaner version and will make it possible to adapt :class:`measurement.Measurement` more easily for the interferometer experiments.

Structure
---------

The new immproved structure will make use of:

- LMFIT package
- pandas dataframe

So that the fitting will be done with LMFIT models, whereas the data is handled in pandas dataframes. This creates huge advantages for the developer as well as for the user.


Previous Development
--------------------

There have been efforts previously to build a unique own modular :class:`measurement.Measurement` class by Nico. These efforts can be examined in the branch improvements/core.

These following elements were attemted to build:

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


**Column Class**

Methods:

- :code:`reverse()`: reverse order of data
- :code:`__init__(self, desc, data)`
- :code:`__repr__()`: plots :code:`'<column object 'desc' of lenght len(data)>'` or something like that


Variables:

- :code:`columns.data`: holds the data as numpy array in float64
- :code:`columns.desc`: holds the name of the columns heading as string


**Fit Function Class**

Method:

- :code:`fit_function()`
- :code:`find_bounds()`: tries to find the bounds
- :code:`bounds`: holds the bounds to be used when fitting as array of tuples

Variables:

- :code:`parameters`: dictionary holding the names of the parameters and the parameters themselves


**Fit Class**

Variables:

- :code:`type` with which function the fit should be carried out, string
- :code:`popt`
- :code:`pcov`

Methods:

- :code:`fit()`

**Data Set Class**

This object stores data points (lists or Column objects) to form a data set. It must contain at least two data point lists. These lists must have the same number of elements, if not the lists that don't have enough elements will get padded with 0.

Variables:

- :code:`desc`: a description of what the data set describes (optional)
- :code:`data`: data is stored in list; len(list) > 1;


It is obvious to every reader that indeed almost all of this functionality is already included in the python package pandas and lmfit. This led to the conclusion that improvements/core won't be maintained any longer.


The brand new Measurement Class
-------------------------------

The brand new measurement class will include only the following featues:

- ready-to-use lmfit fit models
- fit() method to actually produce a fit using lmfits minimize()
- plot() method for implementing plotting functionality
- contrast() to calculate the contrast
- degree_of_polarisation() to calculate the degree of polarisation
- read() to read data in a very generic way
- export_meta() to export meta data

Its child classes will then implement the experiment specific data handling details like cleaning the data and extending the meta data that will be exported.

.. mermaid::

    graph TD
        m[measurement class] --> p[polarimeter class]
        m --> i[interferometer class]
