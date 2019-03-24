# PIGOR

Pigor is a lightweight analysis tool for the NEPTUN beam line at [Atominstitut](https://ati.tuwien.ac.at/startseite/) of [TU Wien](https://www.tuwien.ac.at/), Austria. For more information visit [our homepage](http://www.neutroninterferometry.com/).

**Documentation has moved:** The documentation has moved from this file and other markdown files in the root of this repository to a Sphinx documentation. You can find it under `doc/_build/html` or build it for your own with the `make html` command in the `doc/` directory. 

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

=> TODOs have omoved to the Sphinx documentation.

## How to Install

=> This section was moved to the Sphinx documentation.
