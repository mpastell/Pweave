#!/usr/bin/env python

# Pweave, Report generation with Python
# ============================================
# 
# :Author: Matti Pastell <matti.pastell@helsinki.fi
# :Website: http://mpastell.com
#  Version: 0.2


import sys
sys.path.append('.')
from optparse import OptionParser
import os
import pweave



if len(sys.argv)==1:
    print "This is Pweave, enter Pweave -h for help"
    sys.exit()

# Command line options

parser = OptionParser(usage="%prog [options] sourcefile", version="%prog 0.2")
parser.add_option("-f", "--format", dest="format", default='rst',
                  help="The output format: 'sphinx', 'rst' (default), 'pandoc' or 'tex'")
parser.add_option("-m", "--matplotlib", dest="mplotlib", default=True,
                  help="Do you want to use matplotlib True (default) or False")
parser.add_option("-g", "--figure-format", dest="figfmt",
                  help="Figure format for matplolib graphics: Defaults to 'png' for rst and Sphinx html documents and 'pdf' for tex")
parser.add_option("-d", "--figure-directory", dest="figdir", default = 'images/',
                  help="Directory path for matplolib graphics: Default 'images/'")
(options, args) = parser.parse_args()
infile = args[0]

print options.mplotlib
pweave.pweave(infile, doctype = options.format, plot = options.mplotlib )

