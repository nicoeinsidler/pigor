Using PIGOR in Jupyter
======================


.. note:: Please make sure that you have a running Jupyter or Jupyter Lab installation on your system. For more information, please visit https://jupyter.org/install.

.. note:: Make sure to install all the requirements for the measurement class in `requirements-measurement.txt`. See :ref:`installation` for more details.

First, open a new Jupyter notebook. Make sure that these following files are within the directory where your newly created Jupyter notebook is located:

* measurement.py
* fit_functions.py

If not, you can just copy those two files.

Now we have to import the measurement module in the Jupyter notebook by using the `import` command:

.. code-block:: python

    import measurement

This should already be enough to work with the measurement class within a Jupyter notebook. However there are a few extra steps to take, if one wishes to use inline graphics. To enable this functionality one line has to be added as the first cell to the notebook:

.. code-block:: python

    %matplotlib inline

Now, whenever the plot method is called, an additional argument has to be passed on. 

.. code-block:: python

    m.plot(enable_jupyter=True)

.. note:: A test notebook is provided in the root of the PIGOR project at https://github.com/nicoeinsidler/pigor/blob/master/PIGOR-Test-Notebook.ipynb.