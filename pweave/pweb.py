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

from .mimetypes import MimeTypes


# Python2 compatibility fix
if sys.version_info[0] == 3:
    basestring = str


class Pweb(object):
    """Processes a complete document
    :param file: ``string`` name of the input document.
    :param format: ``string`` output format from supported formats. pweavSee: http://mpastell.com/pweave/formats.html
    """

    def __init__(self, source, *, reader = None , doctype = "notebook", kernel = "python",
                 output = None, figdir = 'figures', mimetype = None):
        self.source = source
        name, ext = os.path.splitext(os.path.basename(source))
        self.basename = name
        self.file_ext = ext
        self.figdir = figdir
        self.doctype = doctype
        self.sink = None



        if mimetype is None:
            self.mimetype = MimeTypes.guess_mimetype(self.source)
        else:
            self.mimetype = MimeTypes.get_mimetype(mimetype)


        if self.source != None:
            name, file_ext = os.path.splitext(self.source)
            self.file_ext = file_ext.lower()
        else:
            self.file_ext = None

        self.output = output
        self.setkernel(kernel)
        self._setwd()

        #Init variables not set using the constructor
        #: Use documentation mode
        self.documentationmode = False
        self.parsed = None
        self.executed = None
        self.formatted = None
        self.reader = None
        self.formatter = None
        self.processor = None


        self.read(reader = reader)

    def _setwd(self):
        self.wd = os.path.dirname(self.output if self.output is not None else self.source)

    def setformat(self, doctype = None, Formatter=None):
        """Set output format for the document

        :param doctype: ``string`` output format from supported formats. See: http://mpastell.com/pweave/formats.html
        :param Formatter: Formatter class, can be used to specify custom formatters. See: http://mpastell.com/pweave/subclassing.html

        """
        #Formatters are needed  when the code is executed and formatted



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

    def getformat(self):
        """Get current format dictionary. See: http://mpastell.com/pweave/customizing.html"""
        return self.formatter.formatdict

    def updateformat(self, dict):
        """Update existing format, See: http://mpastell.com/pweave/customizing.html"""
        self.formatter.formatdict.update(dict)

    def read(self, string=None, basename="string_input", reader = None):
        """Parse document
        :param None (set automatically), reader name or class object
        """
        if reader is None:
            Reader = PwebReaders.guess_reader(self.source)
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
                         self.figdir,
                         self.wd
                        )
        proc.run()
        self.processor = proc
        self.executed = proc.getresults()
        self.isexecuted = True

    def format(self, doctype = None, Formatter = None):
        """Format the code for writing. You can pass either
        :doctype The name of Pweave output format
        :Formatter Formatter class
        """
        if doctype is not None:
            Formatter = PwebFormats.getFormatter(doctype)
        elif Formatter is not None:
            Formatter = Formatter
        elif self.doctype is None:
            Formatter = PwebFormats.getFormatter(PwebFormats.guessFromFilename(self.source))
        else:
            Formatter = PwebFormats.getFormatter(self.doctype)

        self.formatter = Formatter(self.executed,
                                   kernel = self.kernel,
                                   language = self.language,
                                   mimetype = self.mimetype.type)


        self.formatter.format()
        self.formatted = self.formatter.getformatted()

    def setsink(self):
        if self.output is None:
            self.sink = os.path.splitext(self.source)[0] + '.' + self.formatter.file_ext
        else:
            self.sink = self.output


    def _getDstExtension(self):
        return self.formatter.getformatdict()['extension']

    def write(self, action="Pweaved"):
        """Write formatted code to file"""
        self.setsink()

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
