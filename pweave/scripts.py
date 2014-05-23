from __future__ import print_function, division

import sys
from optparse import OptionParser
import os
import pweave


def weave():

    if len(sys.argv)==1:
        print("This is Pweave %s, enter Pweave -h for help" % pweave.__version__)
        sys.exit()

# Command line options
    parser = OptionParser(usage="Pweave [options] sourcefile", version="Pweave " + pweave.__version__)
    parser.add_option("-f", "--format", dest="format", default='rst',
                      help="The output format. Available formats: " + pweave.PwebFormats.shortformats() + " Use Pweave -l to list descriptions or see http://mpastell.com/pweave/formats.html")
    parser.add_option("-i", "--input-format", dest="informat", default='noweb',
                      help="Input format: noweb, notebook or script")
    parser.add_option("-s", "--shell", dest="shell", default='python',
                      help="shell used to run code: python or ipython")
    parser.add_option("-l","--list-formats", dest="listformats", action = "store_true" ,default=False,
                      help="List output formats")
    parser.add_option("-m", "--matplotlib", dest="mplotlib", default='true',
                      help="Do you want to use matplotlib (or Sho with Ironpython) True (default) or False")
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
                      help="Figure format for matplotlib graphics: Defaults to 'png' for rst and Sphinx html documents and 'pdf' for tex")

    (options, args) = parser.parse_args()

    try:
        infile = args[0]
    except:
        infile = ""



    mplotlib = (options.mplotlib.lower() == 'true')

    if options.figfmt is not None:
        figfmt = ('.%s' % options.figfmt)
    else:
        figfmt = None

    pweave.pweave(infile, doctype = options.format, informat=options.informat, shell=options.shell, plot = mplotlib,
           docmode = options.docmode, cache = options.cache, figdir = options.figdir,
           cachedir = options.cachedir, figformat = figfmt, listformats = options.listformats)

def publish():
    if len(sys.argv)==1:
        print("Publish a python script. Part of Pweave %s, use -h for help" % pweave.__version__)

        sys.exit()
    parser = OptionParser(usage="pypublish [options] sourcefile", version="Part of Pweave " + pweave.__version__)
    parser.add_option("-f", "--format", dest="format", default='html',
                      help = "Output format html or pdf, pdf output requires pandoc and pdflatex")

    (options, args) = parser.parse_args()

    try:
        infile = args[0]
    except:
        infile = ""

    pweave.publish(infile, options.format)

def tangle():
    if len(sys.argv)==1:
        print("This is Ptangle %s" % pweave.__version__)
        print("Usage: Ptangle file")
        sys.exit()

    pweave.ptangle(sys.argv[1])

def convert():
    if len(sys.argv)==1:
        print("This is Pweave document converter %s. Enter Pweave-convert -h for help " % pweave.__version__)
        sys.exit()

    parser = OptionParser(usage="Pweave-convert [options] sourcefile", version="Part of Pweave " + pweave.__version__)
    parser.add_option("-i", "--input-format", dest="informat", default='noweb',
                      help="Input format: noweb, notebook or script")
    parser.add_option("-f", "--output-format", dest="outformat", default='html',
                      help = "Output format script or noweb")
    parser.add_option("-p", "--pandoc", dest="pandoc_args", default=None,
                      help = "passed to pandoc for converting doc chunks")

    (options, args) = parser.parse_args()

    infile = args[0]

    #print options
    pweave.convert(infile, options.informat, options.outformat, options.pandoc_args)


