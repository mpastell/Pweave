#!/usr/bin/env bash

set -e -x

wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
chmod +x miniconda.sh
./miniconda.sh -b
export PATH=/home/travis/miniconda3/bin:$PATH
conda update --yes conda
