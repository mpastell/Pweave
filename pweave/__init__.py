# Python module Pweave
# Matti Pastell 2010-2013
# http://mpastell.com/pweave

from pweb import *
import time
import readers
import markdown
import templates
import os
from subprocess import Popen, PIPE

__version__ = '0.22b'


def pweave(file, doctype = 'rst', informat = "noweb", plot = True,
           docmode = False, cache = False,
           figdir = 'figures', cachedir = 'cache',
           figformat = None, returnglobals = True, listformats = False):
    """
    Processes a Pweave document and writes output to a file

    :param file: ``string`` input file
    :param doctype: ``string`` output document format: call with listformats true to get list of supported formats.
    :param informat: ``string`` input format: "noweb" or "script"
    :param plot: ``bool`` use matplotlib (or Sho with Ironpython) 
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
    
    if informat=="noweb":
        doc.setreader(readers.PwebReader)
    if informat=="script":
        doc.setreader(readers.PwebScriptReader)


    if sys.platform == 'cli':
        Pweb.usesho = plot
        Pweb.usematplotlib = False
    else:
        Pweb.usematplotlib = plot
    
    Pweb.figdir = figdir
    Pweb.cachedir = cachedir
    doc.documentationmode = docmode
    doc.storeresults = cache

    if figformat is not None:
        doc.updateformat({'figfmt' : figformat, 'savedformats' : [figformat]})
        
    #Returning globals
    try:
        doc.weave()
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
        caller.f_globals.update(Pweb.globals)
    if not hasattr(sys,'_getframe'):
        print('%s\n%s\n' % ("Can't return globals" ,"Start Ironpython with ipy -X:Frames if you wan't this to work"))

def ptangle(file):
    """Tangles a noweb file i.e. extracts code from code chunks to a .py file
    
    :param file: ``string`` the pweave document containing the code
    """
    doc = Pweb(file)
    doc.tangle()

def publish(file, format = "html"):
    """Publish python script and results to html or pdf"""

    if format == "html":
        pformat = "md2html"
        Pweb.defaultoptions.update({"wrap" : False})
    elif format == "pdf":
        pformat = "pandoc2latex"
    else:
        print "Unknown format, exiting"
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
            print "Running pdflatex..."
        except:
           print "Can't find pdflatex, no pdf produced!"
           return
        x = latex.communicate()[0]
        print ("\n").join(x.splitlines()[-2:])

def spin(file):
    """Convert input file from script format to noweb format, similar to Knitr's spin."""
    doc = readers.PwebConvert(file)
    
def convert(file, informat="noweb", outformat="script", pandoc_args=None):
    """Convert input file from script to noweb or vice versa"""
    doc = readers.PwebConvert(file, informat, outformat, pandoc_args)
    



    
 

    
    