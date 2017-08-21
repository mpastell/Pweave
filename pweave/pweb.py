import sys
import os
import re
import copy
import io

from .readers import PwebReaders
from . formatters import PwebFormats
from . processors import PwebProcessors
from jupyter_client import kernelspec

from .mimetypes import MimeTypes
from urllib import parse


class Pweb(object):
    """
    Process a Pweave document

    :param source: ``string`` name of the input document.
    :param doctype: ``string`` output format.
    :param informat: ``string`` input format
    :param kernel: ``string`` name of jupyter kernel used to run code
    :param output: ``string`` output path
    :param figdir: ``string`` figure directory
    :param mimetype: Source document's text mimetype. This is used to set cell
                     type in Jupyter notebooks
    """

    def __init__(self, source, doctype = None, *, informat = None, kernel = "python3",
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

        if kernel is not None:
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
        self.theme = "skeleton"

        self.setformat(doctype)
        self.read(reader = informat)

    def _setwd(self):
        if self.output is not None:
            self.wd = os.path.dirname(self.output)
        elif parse.urlparse(self.source).scheme == "":
            self.wd = os.path.dirname(self.source)
        else:
            self.wd = "."

    def setkernel(self, kernel):
        """Set the kernel for jupyter_client"""
        self.kernel = kernel
        self.language = kernelspec.get_kernel_spec(kernel).language

    def getformat(self):
        """Get current format dictionary. See: http://mpastell.com/pweave/customizing.html"""
        return self.formatter.formatdict

    def updateformat(self, dict):
        """Update existing format, See: http://mpastell.com/pweave/customizing.html"""
        self.formatter.formatdict.update(dict)

    def read(self, string=None, basename="string_input", reader = None):
        """
        Parse document

        :param: None (set automatically), reader name or class object
        """
        if reader is None:
            Reader = PwebReaders.guess_reader(self.source)
        elif isinstance(reader, str):
            Reader = PwebReaders.get_reader(reader)
        else:
            Reader = reader


        if string is None:
            self.reader = Reader(file=self.source)
        else:
            self.reader = self.Reader(string=string)
            self.source = basename # non-trivial implications possible
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
        self.executed = proc.getresults()

    def setformat(self, doctype = None, Formatter = None):
        """
        Set formatter by name or class. You can pass either

        :param doctype: The name of Pweave output format
        :param Formatter: Formatter class
        """

        if doctype is not None:
            Formatter = PwebFormats.getFormatter(doctype)
        elif Formatter is not None:
            Formatter = Formatter
        elif self.doctype is None:
            Formatter = PwebFormats.getFormatter(PwebFormats.guessFromFilename(self.source))
        else:
            Formatter = PwebFormats.getFormatter(self.doctype)

        self.formatter = Formatter([],
                                   kernel = self.kernel,
                                   language = self.language,
                                   mimetype = self.mimetype.type,
                                   source = self.source,
                                   theme = self.theme,
                                   figdir = self.figdir,
                                   wd = self.wd)


    def format(self):
        """Format executed code for writing. """
        self.formatter.executed = copy.deepcopy(self.executed)
        self.formatter.format()
        self.formatted = self.formatter.getformatted()

    def setsink(self):
        if self.output is not None:
            self.sink = self.output
        elif parse.urlparse(self.source).scheme == "":
            self.sink = os.path.splitext(self.source)[0] + '.' + self.formatter.file_ext
        else:
            url_path = parse.urlparse(self.source).path
            self.sink = os.path.splitext(os.path.basename(url_path))[0] + '.' + self.formatter.file_ext

    def write(self):
        """Write formatted code to file"""
        self.setsink()

        self._writeToSink(self.formatted.replace("\r", ""))
        self._print('Weaved {src} to {dst}\n'.format(src=self.source,
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
        if self.output is None:
            target = os.path.join(self.wd, self.basename + '.py')
        code = [x for x in self.parsed if x['type'] == 'code']
        main = '\nif __name__ == "__main__":'
        for x in code:
            if 'main' in x['options'] and x['options']['main']:
                x['content'] = x['content'].replace("\n", "\n    ")
                x['content'] = "".join([main, x['content']])
        code = [x['content'] for x in code]
        f = open(target, 'w')
        f.write('\n'.join(code))
        f.close()
        print('Tangled code from {src} to {dst}'.format(src=self.source,
                                                              dst=target))
