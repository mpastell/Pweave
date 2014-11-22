from __future__ import print_function, division, absolute_import, unicode_literals
import copy

import sys
from optparse import OptionParser
import pweave


def weave():
    if len(sys.argv) == 1:
        print("This is Pweave %s, enter Pweave -h for help" % pweave.__version__)
        sys.exit()

    # Command line options
    parser = OptionParser(usage="Pweave [options] sourcefile", version="Pweave " + pweave.__version__)
    parser.add_option("-f", "--format", dest="doctype", default='rst',
                      help="The output format. Available formats: " + pweave.PwebFormats.shortformats() +
                           " Use Pweave -l to list descriptions or see http://mpastell.com/pweave/formats.html")
    parser.add_option("-i", "--input-format", dest="informat", default='noweb',
                      help="Input format: noweb, notebook or script")
    parser.add_option("-s", "--shell", dest="shell", default='python',
                      help="shell used to run code: python, epython (external python shell), ipython, matlab or octave")
    parser.add_option("--shell-path", dest="shell_path", default=None,
                      help="Set the path of shell to run code, only affects \"epython\" shell")
    parser.add_option("-l", "--list-formats", dest="listformats", action="store_true", default=False,
                      help="List output formats")
    parser.add_option("-m", "--matplotlib", dest="plot", default=True, action="store_false",
                      help="Disable matplotlib")
    parser.add_option("-d", "--documentation-mode", dest="docmode",
                      action="store_true", default=False,
                      help="Use documentation mode, chunk code and results will be loaded from cache and inline code will be hidden")
    parser.add_option("-c", "--cache-results", dest="cache",
                      action="store_true", default=False,
                      help="Cache results to disk for documentation mode")
    parser.add_option("-F", "--figure-directory", dest="figdir", default='figures',
                      help="Directory path for matplolib graphics: Default 'figures'")
    parser.add_option("--cache-directory", dest="cachedir", default='cache',
                      help="Directory path for cached results used in documentation mode: Default 'cache'")
    parser.add_option("-g", "--figure-format", dest="figformat", default=None,
                      help="Figure format for matplotlib graphics: Defaults to 'png' for rst and Sphinx html documents and 'pdf' for tex")

    (options, args) = parser.parse_args()

    try:
        infile = args[0]
    except IndexError:
        infile = ""

    opts_dict = vars(options)
    if options.figformat is not None:
        opts_dict["figformat"] = ('.%s' % options.figformat)

    pweave.weave(infile, **opts_dict)


def publish():
    if len(sys.argv) == 1:
        print("Publish a python script. Part of Pweave %s, use -h for help" % pweave.__version__)
        sys.exit()

    parser = OptionParser(usage="pypublish [options] sourcefile", version="Part of Pweave " + pweave.__version__)
    parser.add_option("-f", "--format", dest="format", default='html',
                      help="Output format html or pdf, pdf output requires pandoc and pdflatex")

    (options, args) = parser.parse_args()

    try:
        infile = args[0]
    except IndexError:
        infile = ""

    pweave.publish(infile, options.format)


def tangle():
    if len(sys.argv) == 1:
        print("This is Ptangle %s, enter Ptangle -h for help" % pweave.__version__)
        sys.exit()

    parser = OptionParser(usage="Ptangle sourcefile", version="Pweave " + pweave.__version__)

    (options, args) = parser.parse_args()

    try:
        infile = args[0]
    except IndexError:
        infile = ""

    pweave.tangle(infile)


def convert():
    if len(sys.argv) == 1:
        print("This is Pweave document converter %s. Enter Pweave-convert -h for help " % pweave.__version__)
        sys.exit()

    parser = OptionParser(usage="Pweave-convert [options] sourcefile", version="Part of Pweave " + pweave.__version__)
    parser.add_option("-i", "--input-format", dest="informat", default='noweb',
                      help="Input format: noweb, notebook or script")
    parser.add_option("-f", "--output-format", dest="outformat", default='html',
                      help="Output format script, noweb or notebook")
    parser.add_option("-l", "--list-formats", dest="listformats", action="store_true", default=False,
                      help="List input / output formats")
    parser.add_option("-p", "--pandoc", dest="pandoc_args", default=None,
                      help="passed to pandoc for converting doc chunks")

    (options, args) = parser.parse_args()

    try:
        infile = args[0]
    except IndexError:
        infile = ""

    pweave.convert(file=infile,
                   informat=options.informat,
                   outformat=options.outformat,
                   pandoc_args=options.pandoc_args,
                   listformats=options.listformats)
