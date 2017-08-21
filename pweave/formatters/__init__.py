from .tex import PwebTexFormatter, PwebMintedFormatter, \
                 PwebTexPweaveFormatter, PwebTexPygmentsFormatter
from .rst import  PwebRstFormatter, PwebSphinxFormatter
from .markdown import PwebLeanpubFormatter, PwebPandocFormatter, PwebSoftCoverFormatter
from .publish import  PwebMDtoHTMLFormatter, PwebPandocMDtoHTMLFormatter,\
    PwebPandoctoTexFormatter, PwebHTMLFormatter
from .jupyter_notebook import PwebNotebookFormatter
import os

class PwebFormats(object):
    """Contains a dictionary of available output formats"""
    formats = {'tex': {'class': PwebTexFormatter,
                       'description': 'Latex with verbatim for code and results'},
               'texminted': {'class': PwebMintedFormatter,
                             'description': 'Latex with predefined minted environment for codeblocks'},
               'texpweave': {'class': PwebTexPweaveFormatter,
                             'description': 'Latex output with user defined formatting using named environments (in latex header)'},
               'texpygments': {'class': PwebTexPygmentsFormatter,
                               'description': 'Latex output with pygments highlighted output'},
               'rst': {'class': PwebRstFormatter,
                       'description': 'reStructuredText'},
               'pandoc': {'class': PwebPandocFormatter,
                          'description': 'Pandoc markdown'},
               'markdown': {'class': PwebPandocFormatter, 'description':
                   'Pandoc markdown, same as format pandoc'},
               'leanpub': {'class': PwebLeanpubFormatter,
                           'description': 'Leanpub markdown'},
               'sphinx': {'class': PwebSphinxFormatter,
                          'description': 'reStructuredText for Sphinx'},
               'html': {'class': PwebHTMLFormatter,
                        'description': 'HTML with pygments highlighting'},
               'md2html': {'class': PwebMDtoHTMLFormatter,
                           'description': 'Markdown to HTML using Python-Markdown'},
               'softcover': {'class': PwebSoftCoverFormatter,
                            'description': 'SoftCover markdown'},
               'pandoc2latex': {'class': PwebPandoctoTexFormatter,
                                'description': 'Markdown to Latex using Pandoc, requires Pandoc in path'},
               'pandoc2html': {'class': PwebPandocMDtoHTMLFormatter,
                               'description': 'Markdown to HTML using Pandoc, requires Pandoc in path'},
               'notebook': {'class': PwebNotebookFormatter,
                               'description': 'Jupyter notebook'}
                }

    @classmethod
    def getFormatter(cls, doctype):
        return cls.formats[doctype]['class']

    @classmethod
    def guessFromFilename(cls, filename):
        _, ext = os.path.splitext(filename)
        return cls.guessFromExtension(ext.lower())

    @staticmethod
    def guessFromExtension(ext):
        if ext in ('.pmd', '.py'): return 'markdown'
        if 'md' in ext: return 'markdown'
        if 'tex' in ext: return 'texpygments'
        if 'rst' in ext: return 'rst'
        if 'htm' in ext: return 'html'

        print("Can't autodetect output format, defaulting to markdown")
        return 'markdown'

    @classmethod
    def shortformats(cls):
        fmtstring = ""
        names = list(cls.formats.keys())
        n = len(names)
        for i in range(n):
            fmtstring += " %s" % (names[i])
            if i < (n - 1):
                fmtstring += ","

        return fmtstring

    @classmethod
    def getformats(cls):
        fmtstring = ""
        for format in sorted(cls.formats):
            fmtstring += "* %s:\n   %s\n" % (format, cls.formats[format]['description'])
        return fmtstring

    @classmethod
    def listformats(cls):
        print("\nPweave supported output formats:\n")
        print(cls.getformats())
