Measurement Class 2.0
=====================

Due to some design flaws in the existsing :class:`measurement.Measurement` class, it will be rewritten from ground up using already existsing libraries. This undertaking will lead to a cleaner version and will make it possible to adapt :class:`measurement.Measurement` more easily for the interferometer experiments.

Structure
---------

The new immproved structure will make use of:

- LMFIT package
- pandas dataframe

So that the fitting will be done with LMFIT models, whereas the data is handled in pandas dataframes. This creates huge advantages for the developer as well as for the user.


Development
-----------

There have been efforts previously to build a unique own modular :class:`measurement.Measurement` class by Nico. These efforts can be examined in the branch improvements/core.

