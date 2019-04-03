How to install PIGOR
====================


Installing PIGOR
----------------

Assuming you have a running installation of **Python 3.7** or higher, to install PIGOR please follow these steps:

1. Download the source from Bitbucket with :code:`git clone https://github.com/nicoeinsidler/pigor.git`. This should include (at least) the following files:
    - :code:`measurement.py`
    - :code:`pigor.py`
    - :code:`README.md`
    - :code:`requirements.py`
    - :code:`requirements-dev.py`
    - :code:`requirements-measurement.py`
2. Install the requirements with::

    pip install -r requirements.txt

.. note:: If you are using two separate python 2.x and 3.x installations, you might need to use :code:`pip3` instead of :code:`pip`.

You can now run PIGOR with the following command in the folder where the :code:`pigor.py` and :code:`measurement.py` files are located::

    python pigor.py

.. note:: If you only want to use the :class:`measurement.Measurement` class, you can only install it's dependencies with :code:`pip install -r requirements-measurement.txt`. But since most dependencies are shared, it won't make much of a difference.

Installing only the Measurement Class
-------------------------------------

.. warning:: This is not maintained yet. Please use this feature with caution and build it first.

In some cases the user may only want to install the measurement module to use the Measurement class as one of their python installations modules. A zip or tarball file should be provided for this use case. See :ref:`deployment-measurement-module`.

To install (and copy into the user's installed modules) simply unpack the zip or tarball. Head over to its directory and type from there:

.. code-block:: bash

    python setup.py install


Installation for Developers
---------------------------

A known working set of python modules used to create PIGOR can be found in :code:`requirements-dev.txt`. To install all these requirements, simply type::

    pip install -r requirements-dev.txt

It is recommended to use a virtual environment.