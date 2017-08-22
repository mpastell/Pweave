# Python module Pweave
# Matti Pastell 2010-2016
# http://mpastell.com/pweave


from . import readers
from .pweb import *
from .formatters import *
from .readers import *
from .processors import *
from .config import *


__version__ = '0.30rc1'


def weave(file, doctype=None, informat=None, kernel="python3", plot=True,
          docmode=False, cache=False,
          figdir='figures', cachedir='cache',
          figformat=None, listformats=False,
          output=None, mimetype=None,):
    """
    Processes a Pweave document and writes output to a file

    :param file: ``string`` input file
    :param doctype: ``string`` output document format: call with listformats true to get list of supported formats.
    :param informat: ``string`` input format: "noweb", "markdown", "notebook" or "script"
    :param kernel: ``string`` Jupyter kernel used to run code: default is python3
    :param plot: ``bool`` use matplotlib
    :param docmode: ``bool`` use documentation mode, chunk code and results will be loaded from cache and inline code will be hidden
    :param cache: ``bool`` Cache results to disk for documentation mode
    :param figdir: ``string`` directory path for figures
    :param cachedir: ``string`` directory path for cached results used in documentation mode
    :param figformat: ``string`` format for saved figures (e.g. '.png'), if None then the default for each format is used
    :param listformats: ``bool`` List available formats and exit
    :param output: ``string`` output file
    :param mimetype: ``string`` Source document's text mimetype. This is used to set cell
                                type in Jupyter notebooks.
    """

    if listformats:
        PwebFormats.listformats()
        return

    if figformat is not None:
        sys.stdout.write("figformat option is not implemented for Pweave >= 0.3")

    assert file != "" is not None, "No input specified"

    doc = Pweb(file, informat=informat, doctype=doctype,
               kernel=kernel, output=output, figdir=figdir,
               mimetype=mimetype
               )
    doc.documentationmode = docmode

    rcParams["usematplotlib"] = plot
    rcParams["cachedir"] = cachedir
    rcParams["storeresults"] = cache

    doc.weave()

def tangle(file, informat = None):
    """Tangles a noweb file i.e. extracts code from code chunks to a .py file

    :param file: ``string`` the pweave document containing the code
    """
    doc = Pweb(file, kernel = None, informat = informat)
    doc.tangle()


def publish(file, doc_format="html", theme="skeleton", latex_engine="pdflatex",
            output = None):
    """Publish python script and results to html or pdf, expects that doc
    chunks are  written in markdown.

    :param file: ``string`` input file"
    :param format: ``string`` output format "html" of "pdf", pdf output
            requires pandoc and pdflatex in your path.
    :param latex_engine: ``string`` the command for running latex. Defaults to "pdflatex".
    :param output: ``string`` output file. Use .tex extension for pdf output.
    """

    if doc_format == "html":
        pformat = "md2html"
    elif doc_format == "pdf":
        pformat = "pandoc2latex"
    else:
        print("Unknown format, exiting")
        return

    doc = Pweb(file, kernel="python3", doctype=pformat,
               output=output)

    doc.theme = theme

    doc.read()
    doc.run()
    doc.format()

    doc.write()
    if doc_format == "pdf":
        try:
            latex = Popen([latex_engine, doc.sink], stdin=PIPE, stdout=PIPE)
            print("Running " + latex_engine + "...")
        except:
            print("Can't find " + latex_engine + ", no pdf produced!")
            return
        x = latex.communicate()[0].decode('utf-8')
        print("\n".join(x.splitlines()[-2:]))


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


def listformats():
    """List output formats"""
    PwebFormats.listformats()
