Measurement Naming Convention
=============================

In order for the Measurement class to work properly, the user should follow this naming convention:

:code:`YYYY_MM_DD_HHmm_IDENTIFIER_TYPE.dat` (not case sensitive)

where...

- :code:`IDENTIFIER` denotes the type of measurement or the reason for the measurement. The following values are common and recognized by PIGOR:
    - :code:`dcX#`: DC coil (for the magnetic field in x-direction) scan for the DC coil with the number #. A sine fit is automatically applied, when :code:`TYPE` is not set.
    - :code:`dcZ#`: DC coil scan in z-direction (compensation field) for DC coil number #. Fitted with a polynomial of order 5 by default.
    - :code:`pos#`: position scan with stage number #. Fitted with a Gaussian by default.
- :code:`TYPE` specifies and overrides the type of fitting/analysis that should be applied by PIGOR. Possible values:
    - fitting types
        - :code:`poly5`: polynom of order 5
        - :code:`sine_lin`: sine plus additional added linear function
        - :code:`sine`: sine
        - :code:`gauss`: Gauß fit
    - special analysis types
        - :code:`pol`: specifies that this measurement is a degree of polarisation measurement. This will automatically calculate the degree of polarisation for any given number of points (number of data points must be multiple of four)

Types can be combined within a types group (gauss and pol for example, like "gauss_pol" or "pol_gauss").