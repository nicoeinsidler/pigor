.. PIGOR documentation master file, created by
   sphinx-quickstart on Wed Mar 20 17:14:07 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to PIGOR's documentation!
=================================

Pigor is a lightweight analysis tool for the NEPTUN beam line at `Atominstitut`_ of `TU Wien`_, Austria. For more information visit `our homepage`_.

.. _Atominstitut: https://ati.tuwien.ac.at/startseite/
.. _TU Wien: https://www.tuwien.ac.at/
.. _our homepage: http://www.neutroninterferometry.com/

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   naming-convention
   quickstart
   pigor
   measurement
   deployment



PIGOR & Measurement Class ToDos
-------------------------------

Here are all ToDos listed. Feel free to contribute and check this project out on Bitbucket.

- self.x_error: not yet implemented
- a lot of commenting
- error of fit
- verbose mode on/off
- getting PIGOR ready for shipment by creating a setup.py
- better display of self.pcov
- separation between pure functions and functions with context (methods)
- auto comment decorator for functions
- use decorators to auto register fit functions with their input argument list
- setuptools in setup.py
- https://click.palletsprojects.com/en/7.x/quickstart/
- requirements.txt


Sphinx documentation ToDos
--------------------------

.. todolist::


Project Dependencies
--------------------

.. todo:: check if dependencies are correct with dependencies.txt

- numpy
- re
- matplotlib
- os.path
- glob
- difflib
- datetime
- pathlib
- scipy
- markdown


Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
