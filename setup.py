#!/usr/bin/env python
from setuptools import setup
import os
import pweave
import sys


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='Pweave',
      entry_points={
          'console_scripts':
              ['Pweave = pweave.scripts:weave',
               'pweave = pweave.scripts:weave',
               'Ptangle = pweave.scripts:tangle',
               'ptangle = pweave.scripts:tangle',
               'pypublish = pweave.scripts:publish',
               'pweave-convert = pweave.scripts:convert'
               ]},
      version = pweave.__version__,
      description='Scientific reports with embedded python computations with reST, LaTeX or markdown',
      author='Matti Pastell',
      author_email='matti.pastell@helsinki.fi',
      url='http://mpastell.com/pweave',
      packages=['pweave',
                'pweave._Python{.version_info.major}'.format(sys),
                'pweave.themes',
                'pweave.formatters',
                'pweave.formatters._Python{.version_info.major}'.format(sys),
                'pweave.processors',
                ],
      license='LICENSE.txt',
      long_description = read('README.rst'),
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Topic :: Text Processing :: Markup',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Documentation',
        'Topic :: Documentation :: Sphinx',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5'
        ]

)
