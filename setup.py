#!/usr/bin/env python
from setuptools import setup
import os
import ast

HERE = os.path.abspath(os.path.dirname(__file__))

def get_version():
    """Get version."""
    with open(os.path.join(HERE, 'pweave', '__init__.py'), 'r') as f:
        data = f.read()
    lines = data.split('\n')
    for line in lines:
        if line.startswith('__version__'):
            version_tuple = ast.literal_eval(line.split('=')[-1].strip())
            version = ''.join(map(str, version_tuple))
            break
    return version


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='Pweave',
      entry_points={
          'console_scripts':
              ['pweave = pweave.scripts:weave',
               'ptangle = pweave.scripts:tangle',
               'pypublish = pweave.scripts:publish',
               'pweave-convert = pweave.scripts:convert'
               ]},
      version = get_version(),
      description='Scientific reports with embedded python computations with reST, LaTeX or markdown',
      author='Matti Pastell',
      author_email='matti.pastell@helsinki.fi',
      url='http://mpastell.com/pweave',
      packages=['pweave', 'pweave.themes', 'pweave.formatters', 'pweave.processors'],
      install_requires = ['markdown', 'pygments', 'ipython', 'nbformat',
                          'nbconvert', 'jupyter_client', 'ipykernel'],
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
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        ]

)
