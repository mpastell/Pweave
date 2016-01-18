#!/bin/bash
nosetests --with-cov --cover-package=pweave --cover-html -v
#run with Python 3.5 using conda env
source activate pweave_35
nosetests
