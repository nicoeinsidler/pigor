Measurement Class
=================

This document will keep track of the structure the measurement class has and how it functions.

Structure of a Measurement Object
---------------------------------

Internal variables:

| name                  | description                                                                       |
| --------------------- | --------------------------------------------------------------------------------- |
| self.N_HEADER         |                                                                                   |
| self.path             |                                                                                   |
| self.type_of_fit      |
| self.fit_fuction_list |
| self.raw:             | contains the raw dat file                                                         |
| self.head:            | contains the raw header of the dat file                                           |
| self.data             | contains the raw data as numpy array of floats of the dat file without the header |
| self.desc             | last line of self.head used for axis labels                                       |
| self.settings         | dictionary holding useful information gathered from dat file, like timestamp      |
| self.x                |
| self.y                |
| self.y_error          |


Methods: