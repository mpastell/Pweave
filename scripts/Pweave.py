#!/usr/bin/env python

# Pweave, Report generation with Python
# =====================================
# 
# :Author: Matti Pastell <matti.pastell@helsinki.fi
# :Website: http://mpastell.com/pweave
#  Version: 0.2

import sys
from optparse import OptionParser
import os
from pweave import pweave



if len(sys.argv)==1:
    print "This is Pweave, enter Pweave -h for help"
    sys.exit()

# Command line options
parser = OptionParser(usage="%prog [options] sourcefile", version="%prog 0.2")
parser.add_option("-f", "--format", dest="format", default='rst',
                  help="The output format: 'sphinx', 'rst' (default), 'pandoc' or 'tex'")
parser.add_option("-m", "--matplotlib", dest="mplotlib", default='true',
                  help="Do you want to use matplotlib (or Sho with Ironpython) True (default) or False")
parser.add_option("--use-minted", "--minted", action="store_true", dest="minted", help="Use minted package for code chunks in LaTeX documents", default=False)
parser.add_option("-d","--documentation-mode", dest="docmode", 
                  action = "store_true" ,default=False,
                  help="Use documentation mode, chunk code and results will be loaded from cache and inline code will be hidden")
parser.add_option("-c","--cache-results", dest="cache", 
                  action = "store_true", default=False,
                  help="Cache results to disk for documentation mode")
parser.add_option("--figure-directory", dest="figdir", default = 'figures',
                  help="Directory path for matplolib graphics: Default 'figures'")
parser.add_option("--cache-directory", dest="cachedir", default = 'cache',
                  help="Directory path for cached results used in documentation mode: Default 'cache'")
parser.add_option("-g","--figure-format", dest="figfmt",
                  help="Figure format for matplolib graphics: Defaults to 'png' for rst and Sphinx html documents and 'pdf' for tex")

(options, args) = parser.parse_args()
infile = args[0]
mplotlib = (options.mplotlib.lower() == 'true')

if options.figfmt is not None:
    figfmt = ('.%s' % options.figfmt)
else:
    figfmt = None

#print options.figfmt

pweave(infile, doctype = options.format, plot = mplotlib,
       useminted = options.minted, docmode = options.docmode,
       cache = options.cache, figdir = options.figdir,
       cachedir = options.cachedir, figformat = figfmt)

