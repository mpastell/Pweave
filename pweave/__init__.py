# Python module Pweave
# Matti Pastell 2010-2013
# http://mpastell.com/pweave

from __future__ import print_function, division, unicode_literals, absolute_import


import inspect
from . import readers
from .pweb import *
from .formatters import *
from .readers import *
from .processors import *
from .config import *
import copy

__version__ = '0.23'

def weave(file, doctype='rst', informat="noweb", shell="python", shell_path=None, plot=True,
           docmode=False, cache=False,
           figdir='figures', cachedir='cache',
           figformat=None, returnglobals=True, listformats=False):

#def weave(file, doctype='rst', informat="noweb", shell="python", shell_path=None, plot=True,
#           docmode=False, cache=False,
#           figdir='figures', cachedir='cache',
#           figformat=None, returnglobals=True, listformats=False):
    """
    Processes a Pweave document and writes output to a file

    :param file: ``string`` input file
    :param doctype: ``string`` output document format: call with listformats true to get list of supported formats.
    :param informat: ``string`` input format: "noweb" or "script"
    :param shell: ``string`` shell used to run code: "python" or "ipython"
    :param shell_path: ``string`` Set the path of shell to run code, only affects "epython" shell
    :param plot: ``bool`` use matplotlib
    :param docmode: ``bool`` use documentation mode, chunk code and results will be loaded from cache and inline code will be hidden
    :param cache: ``bool`` Cache results to disk for documentation mode
    :param figdir: ``string`` directory path for figures
    :param cachedir: ``string`` directory path for cached results used in documentation mode
    :param figformat: ``string`` format for saved figures (e.g. '.png'), if None then the default for each format is used
    :param returnglobals: ``bool`` if True the namespace of the executed document is added to callers global dictionary. Then it is possible to work interactively with the data while writing the document. IronPython needs to be started with -X:Frames or this won't work.
    :param listformats: ``bool`` List available formats and exit
    """

    if listformats:
        PwebFormats.listformats()
        return

    assert file != "" is not None, "No input specified"

    doc = Pweb(file)
    doc.setformat(doctype)
    doc.setreader(readers.PwebReaders.formats[informat]['class'])

    rcParams["usematplotlib"] = plot
    rcParams["figdir"] = figdir
    rcParams["cachedir"] = cachedir
    doc.documentationmode = docmode
    rcParams["storeresults"] = cache
    if shell_path is not None:
        rcParams["shell_path"] = shell_path

    if figformat is not None:
        doc.updateformat({'figfmt': figformat, 'savedformats': [figformat]})

    #Returning globals
    try:
        doc.weave(shell)
        if returnglobals:
        #Get the calling scope and return results to its globals
        #this way you can modify the weaved variables from repl
            _returnglobals()
    except Exception as inst:
        #Return varibles used this far if there is an exception
        if returnglobals:
           _returnglobals()
        raise

def _returnglobals():
    """Inspect stack to get the scope of the terminal/script calling pweave function"""
    if hasattr(sys,'_getframe'):
        caller = inspect.stack()[2][0]
        caller.f_globals.update(PwebProcessorGlobals.globals)
    if not hasattr(sys,'_getframe'):
        print('%s\n%s\n' % ("Can't return globals" ,"Start Ironpython with ipy -X:Frames if you wan't this to work"))

def tangle(file):
    """Tangles a noweb file i.e. extracts code from code chunks to a .py file

    :param file: ``string`` the pweave document containing the code
    """
    doc = Pweb(file)
    doc.tangle()

def publish(file, format = "html"):
    """Publish python script and results to html or pdf, expects that doc
    chunks are  written in markdown.

    ":param file: ``string`` input file"
    ":param format: ``string`` output format "html" of "pdf", pdf output
    requires pandoc and pdflatex in your path.
    """


    if format == "html":
        pformat = "md2html"
        rcParams["chunk"]["defaultoptions"].update({"wrap" : False})
    elif format == "pdf":
        pformat = "pandoc2latex"
    else:
        print("Unknown format, exiting")
        return

    doc = Pweb(file)
    doc.setformat(pformat)
    doc.setreader(readers.PwebScriptReader)
    doc.parse()
    doc.run()
    doc.format()
    doc.write(action = "Published")
    if format == "pdf":
        try:
            latex = Popen(["pdflatex", doc.sink], stdin = PIPE, stdout = PIPE)
            print("Running pdflatex...")
        except:
           print("Can't find pdflatex, no pdf produced!")
           return
        x = latex.communicate()[0].decode('utf-8')
        print(("\n").join(x.splitlines()[-2:]))

def spin(file):
    """Convert input file from script format to noweb format, similar to Knitr's spin."""
    doc = readers.PwebConvert(file)

def convert(file, informat="noweb", outformat="script", pandoc_args=None,
            listformats=False):
    """Convert input file from script to noweb or vice versa

    :param file: ``string`` input file
    :param informat: ``string`` input format noweb, script or notebook
    :param outformat: ``string`` input format noweb or script
    :param pandoc_args: ``string`` arguments passed to pandoc to convert doc chunks.
           e.g. to convert from markdown to latex use: `"-f markdown -t latex"` .
           Note that each doc chunk is converted separately so you can't use pandocs -s option.
    :param listformats: ``bool`` List available formats and exit
    """
    if listformats:
        readers.PwebConverters.listformats()
        return

    Converter = readers.PwebConverters.formats[outformat]['class']
    # pandoc_args = None skips the call to pandoc
    doc = Converter(file, informat, outformat, pandoc_args)
    doc.convert()
    doc.write()
