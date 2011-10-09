#!/usr/bin/env python
from distutils.core import setup
import os

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()



setup(name='Pweave',
      version='0.20',
      description='Scientific reports with embedded python computations with reST, LaTeX or markdown',
      author='Matti Pastell',
      author_email='matti.pastell@helsinki.fi',
      url='http://mpastell.com/pweave',
      packages=['pweave'],
      license=['GPL'],
      scripts=['scripts/Pweave.py', 'scripts/Pweave'],
      classifiers=[
        'Development Status :: 4 - Beta',
        'Topic :: Text Processing :: Markup',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Documentation',
        'License :: OSI Approved :: GNU General Public License (GPL)'],
      long_description = read('README.txt')
)
