from __future__ import print_function, division, unicode_literals, absolute_import
import sys
import os
import re
import copy
import io

from .readers import PwebReader, PwebReaders
from . formatters import PwebFormats
from . processors import PwebProcessors
from .config import rcParams

# Python2 compatibility fix
if sys.version_info[0] == 3:
    basestring = str


class Pweb(object):
    """Processes a complete document
    :param file: ``string`` name of the input document.
    :param format: ``string`` output format from supported formats. pweavSee: http://mpastell.com/pweave/formats.html
    """

    # Shared across class instances
    chunkformatters = []
    chunkprocessors = []

    #: Pweave cache directory
    cachedir = 'cache'

    _mpl_imported = False

    def __init__(self, file=None, format="tex", shell="python",
                 output=None, figdir='figures'):

        #The source document
        self.source = file
        self.sink = None
        self.destination = output
        self.figdir = figdir
        self.doctype = format
        self.parsed = None
        self.executed = None
        self.formatted = None
        self.isparsed = False
        self.isexecuted = False
        self.isformatted = False
        self.kernel = None
        self.language = None

        if self.source != None:
            name, file_ext = os.path.splitext(self.source)
            self.file_ext = file_ext.lower()
        else:
            self.file_ext = None


        if "python" not in shell:
            rcParams["chunk"]["defaultoptions"]["engine"] = shell

        #: Use documentation mode?
        self.documentationmode = False

        self.setreader()
        self.setformat(self.doctype)

    def setformat(self, doctype='tex', Formatter=None, theme = None):
        """Set output format for the document

        :param doctype: ``string`` output format from supported formats. See: http://mpastell.com/pweave/formats.html
        :param Formatter: Formatter class, can be used to specify custom formatters. See: http://mpastell.com/pweave/subclassing.html

        """
        #Formatters are needed  when the code is executed and formatted
        if Formatter is not None:
            self.formatter = Formatter(self)
            return
        #Get formatter class from available formatters
        try:
            Formatter = PwebFormats.getFormatter(doctype)
            self.formatter = Formatter(self) if theme is None else Formatter(self, theme)

        except KeyError as e:
            raise Exception("Pweave: Unknown output format")

    def setkernel(self, kernel):
        """Set the kernel for jupyter_client"""
        self.kernel = kernel


    def setreader(self, Reader=PwebReader):
        """Set class reading for reading documents,
        readers can be used to implement different input markups"""
        if isinstance(Reader, basestring):
            self.Reader = PwebReaders.getReader(Reader)
        else:
            self.Reader = Reader

    def detect_format(self):
        """Detect output format based on file extension"""
        if self.file_ext == ".pmd" or self.file_ext == ".py":
            self.setformat("markdown")
        elif "md" in self.file_ext:
            self.setformat("markdown")
        elif "tex" in self.file_ext:
            self.setformat("texpygments")
        elif "rst" in self.file_ext:
            self.setformat("rst")
        elif "htm" in self.file_ext:
            self.setformat("html")
        else:
            print("Can't autodetect output format, defaulting to reStructured text")
            self.setformat("rst")

    def detect_reader(self):
        """Detect input format based on file extension"""
        if self.file_ext == ".pmd":
            self.setreader("markdown")
        elif self.file_ext == ".py":
            self.setreader("script")
        else:
            self.setreader("noweb")

    def getformat(self):
        """Get current format dictionary. See: http://mpastell.com/pweave/customizing.html"""
        return self.formatter.formatdict

    def updateformat(self, dict):
        """Update existing format, See: http://mpastell.com/pweave/customizing.html"""
        self.formatter.formatdict.update(dict)

    def parse(self, string=None, basename="string_input"):
        """Parse document"""
        if string is None:
            parser = self.Reader(file=self.source)
        else:
            parser = self.Reader(string=string)
            self.source = basename # XXX non-trivial implications possible
        parser.parse()
        self.parsed = parser.getparsed()
        self.isparsed = True

    def run(self, shell="python"):
        """Execute code in the document"""
        if isinstance(shell, basestring):
            Runner = PwebProcessors.getProcessor(shell)
        else:
            Runner = shell

        self.outdir = os.path.dirname(self.destination if self.destination is not None else self.source)

        runner = Runner(copy.deepcopy(self.parsed), self.source,
                        self.documentationmode,
                        self.formatter.getformatdict(),
                        self.figdir,
                        self.outdir,
                        kernel = self.kernel)
        runner.run()
        self.executed = runner.getresults()
        self.isexecuted = True
        self.language = runner.spec["language"]

    def format(self):
        """Format the code for writing"""
        if not self.isexecuted:
            self.run()
        self.formatter.setexecuted(copy.deepcopy(self.executed))
        self.formatter.format()
        self.formatted = self.formatter.getformatted()
        self.isformatted = True

    def _determineOutputFile(self, dst):
        self.sink = dst if dst is not None else \
            (self._basename() + '.' + self._getDstExtension())

    def _getDstExtension(self):
        return self.formatter.getformatdict()['extension']

    def write(self, action="Pweaved"):
        """Write formatted code to file"""
        if not self.isformatted:
            self.format()

        self._determineOutputFile(self.destination)
        self._writeToSink(self.formatted.replace("\r", ""))
        self._print('{action} {src} to {dst}\n'.format(action=action,
                                                       src=self.source,
                                                       dst=self.sink))

    def _print(self, msg):
        sys.stdout.write(msg)

    def _writeToSink(self, data):
        f = io.open(self.sink, 'wt', encoding='utf-8')
        f.write(data)
        f.close()

    def _basename(self):
        return self._getBaseName(self.source)

    def _getBaseName(self, filename):
        return re.split("\.+[^\.]+$", filename)[0]

    def weave(self, shell="python"):
        """Weave the document, equals -> parse, run, format, write"""
        if not self.isparsed:
            self.parse()
        self.run(shell)
        self.format()
        self.write()

    def tangle(self):
        """Tangle the document"""
        self.parse()
        target = self._basename() + '.py'
        code = [x for x in self.parsed if x['type'] == 'code']
        code = [x['content'] for x in code]
        f = open(target, 'w')
        f.write('\n'.join(code))
        f.close()
        self._print('Tangled code from {src} to {dst}'.format(src=self.source,
                                                              dst=target))
