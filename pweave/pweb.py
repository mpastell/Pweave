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
from jupyter_client import kernelspec

# Python2 compatibility fix
if sys.version_info[0] == 3:
    basestring = str


class Pweb(object):
    """Processes a complete document
    :param file: ``string`` name of the input document.
    :param format: ``string`` output format from supported formats. pweavSee: http://mpastell.com/pweave/formats.html
    """

    def __init__(self, source, *, reader = None , doctype = "notebook", kernel = "python",
                 output = None, figdir = 'figures'):
        self.source = source
        name, ext = os.path.splitext(os.path.basename(source))
        self.basename = name
        self.ext = ext
        self.figdir = figdir
        self.setkernel(kernel)

        if doctype is None:
            self._detect_format()
        else:
            self.setformat(doctype)

        self.setsink(output)
        self._setwd()

        if self.source != None:
            name, file_ext = os.path.splitext(self.source)
            self.file_ext = file_ext.lower()
        else:
            self.file_ext = None


        #Kernel setting


        #Init variables not set using the constructor
        #: Use documentation mode
        self.documentationmode = False
        self.parsed = None
        self.executed = None
        self.formatted = None
        self.mimetype = None

        self.read(reader = reader)






    def _setwd(self):
        self.wd = os.path.dirname(self.sink if self.sink is not None else self.source)

    def setformat(self, doctype='tex', Formatter=None, theme = None, mimetype = None):
        """Set output format for the document

        :param doctype: ``string`` output format from supported formats. See: http://mpastell.com/pweave/formats.html
        :param Formatter: Formatter class, can be used to specify custom formatters. See: http://mpastell.com/pweave/subclassing.html

        """
        #Formatters are needed  when the code is executed and formatted
        if Formatter is not None:
            self.formatter = Formatter(self, mimetype = self.mimetype)
            return
        #Get formatter class from available formatters
        try:
            Formatter = PwebFormats.getFormatter(doctype)
            self.formatter = Formatter(self, theme = None)

        except KeyError as e:
            raise Exception("Pweave: Unknown output format")





    def setkernel(self, kernel):
        """Set the kernel for jupyter_client"""
        self.kernel = kernel
        self.language = kernelspec.get_kernel_spec(kernel).language

    def _detect_format(self):
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

    def _detect_reader(self):
        """Detect input format based on file extension"""
        if "md" in self.file_ext:
            return PwebReaders.get_reader("markdown")
        elif self.file_ext == ".py":
            return PwebReaders.get_reader("script")
        else:
            return PwebReaders.get_reader("noweb")

    def getformat(self):
        """Get current format dictionary. See: http://mpastell.com/pweave/customizing.html"""
        return self.formatter.formatdict

    def updateformat(self, dict):
        """Update existing format, See: http://mpastell.com/pweave/customizing.html"""
        self.formatter.formatdict.update(dict)

    def read(self, string=None, basename="string_input", reader = None):
        """Parse document
        :param reader name or class
        """
        if reader is None:
            Reader = self._detect_reader()
        elif isinstance(reader, basestring):
            Reader = PwebReaders.get_reader(reader)
        else:
            Reader = reader

        if string is None:
            self.reader = Reader(file=self.source)
        else:
            self.reader = self.Reader(string=string)
            self.source = basename # XXX non-trivial implications possible
        self.reader.parse()
        self.parsed = self.reader.getparsed()

    def run(self, Processor = None):
        """Execute code in the document"""
        if Processor is None:
            Processor = PwebProcessors.getprocessor(self.kernel)

        proc = Processor(copy.deepcopy(self.parsed),
                         self.kernel,
                         self.source,
                         self.documentationmode,
                         self.formatter.getformatdict(),
                         self.figdir,
                         self.wd
                        )
        proc.run()
        self.processor = proc
        self.executed = proc.getresults()
        self.isexecuted = True

    def format(self):
        """Format the code for writing"""
        self.formatter.setexecuted(copy.deepcopy(self.executed))
        self.formatter.format()
        self.formatted = self.formatter.getformatted()
        self.isformatted = True

    def setsink(self, output = None):
        if output is None:
            self.sink = os.path.splitext(self.source)[0] + '.' + self._getDstExtension()
        else:
            self.sink = output


    def _getDstExtension(self):
        return self.formatter.getformatdict()['extension']

    def write(self, action="Pweaved"):
        """Write formatted code to file"""

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

    def weave(self):
        """Weave the document, equals -> parse, run, format, write"""
        self.run()
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
