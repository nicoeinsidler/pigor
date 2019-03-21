from distutils.core import setup

with open('requirements-measurement.txt') as f:
      requirements = f.readlines()

setup(name='measurement',
      version='1.0',
      description='Measurement Module for NEPTUN, TU Wien',
      author='Nico Einsidler',
      author_email='nicoeinsidler@gmail.com',
      url='www.neutroninterferometry.com/',
      py_modules=['measurement'],
      install_requires=[
            requirements
      ]
      )