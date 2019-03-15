# PIGOR

Pigor is a lightweight analysis tool for the NEPTUN beam line at [Atominstitut](https://ati.tuwien.ac.at/startseite/) of [TU Wien](https://www.tuwien.ac.at/), Austria. For more information visit [our homepage](http://www.neutroninterferometry.com/).

- [PIGOR](#pigor)
  - [Naming Convention](#naming-convention)
  - [TODO](#todo)
  - [How to Install](#how-to-install)

## Naming Convention

All files created at measurements should follow this naming convention:

`YYYY_MM_DD_HHmm_IDENTIFIER_TYPE.dat` (not case sensitive)

where...

- `IDENTIFIER` denotes the type of measurement or the reason for the measurement. The following values are common and recognized by PIGOR:
    - `dcX#`: DC coil (for the magnetic field in x-direction) scan for the DC coil with the number #. A sine fit is automatically applied, when `TYPE` is not set.
    - `dcZ#`: DC coil scan in z-direction (compensation field) for DC coil number #. Fitted with a polynomial of order 5 by default.
    - `pos#`: position scan with stage number #. Fitted with a Gaussian by default.
- `TYPE` specifies and overrides the type of fitting/analysis that should be applied by PIGOR. Possible values:
    - fitting types
        - `poly5`: polynom of order 5
        - `sine_lin`: sine plus additional added linear function
        - `sine`: sine
        - `gauss`: Gauß fit
    - special analysis types
        - `pol`: specifies that this measurement is a degree of polarisation measurement. This will automatically calculate the degree of polarisation for any given number of points (number of data points must be multiple of four)

Types can be combined within a types group (gauss and pol for example, like "gauss_pol" or "pol_gauss").

## TODO

- measurement time in plot
- self.x_error: not yet implemented
- a lot of commenting
- renew docstring style
- ~~fitting boundaries~~
- ~~fixing degree of pol~~
- error of fit
- verbose mode on/off

## How to Install

To 'install' PIGOR, just install Python on your machine and run `python3 pigor.py` in the same directory as the pigor.py file is stored from your preferred bash/shell.

The following python packages should be installed:

- numpy
- re
- matplotlib
- os.path
- glob
- difflib
- datetime
- pathlib
- scipy
