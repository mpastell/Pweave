from .base import PwebFormatter
from .tex import PwebTexPygmentsFormatter
from subprocess import Popen, PIPE
import base64
import sys
import os


class PwebHTMLFormatter(PwebFormatter):
    def format_codechunks(self, chunk):
        from pygments import highlight
        from pygments.lexers import PythonLexer, PythonConsoleLexer, TextLexer
        from pygments.formatters import HtmlFormatter

        chunk['content'] = highlight(chunk['content'], PythonLexer(), HtmlFormatter())
        if len(chunk['result'].strip()) > 0 and chunk['results'] == 'verbatim':
            if chunk['term']:
                chunk['result'] = highlight(chunk['result'], PythonLexer(), HtmlFormatter())
            else:
                chunk['result'] = highlight(chunk['result'], TextLexer(), HtmlFormatter())

        return PwebFormatter.format_codechunks(self, chunk)

    def initformat(self):
        self.formatdict = dict(codestart='',
                               codeend='',
                               outputstart='',
                               outputend='',
                               figfmt='.png',
                               extension='html',
                               width='600',
                               doctype='html')

    def formatfigure(self, chunk):
        result = ""
        figstring = ""
        for fig in chunk['figure']:
            figstring += ('<img src="%s" width="%s"/>\n' % (fig, chunk['width']))

        # Figure environment
        if chunk['caption']:
            # Write labels as data-attribute for javascript etc.
            if chunk['name']:
                labelstring = 'data-label = "fig:%s"' % chunk["name"]
            else:
                labelstring = ""

            result += ("<figure>\n" \
                       "%s"
                       "<figcaption %s>%s</figcaption>\n</figure>" % (figstring, labelstring, chunk['caption']))

        else:
            result += figstring
        return result





class PwebMDtoHTMLFormatter(PwebHTMLFormatter):

    def __init__(self, source = None, theme = "skeleton"):
        from .templates import htmltemplate
        from .. import themes
        from pygments.formatters import HtmlFormatter
        from .. import __version__
        import time
        PwebHTMLFormatter.__init__(self, source)

        if self.source is not None:
            self.path = os.path.dirname(os.path.abspath(self.source))
        else:
             self.path = "."

        theme_css = ""
        try:
            theme_css += getattr(themes, theme)
        except:
            print("Can't find requested theme. Using Skeleton")
            theme_css += getattr(themes, "skeleton")

        self.header = (htmltemplate["header"] %
                {"pygments_css"  : HtmlFormatter().get_style_defs(),
                "theme_css" : theme_css})


        self.footer = (htmltemplate["footer"] %
                       {"source": self.source, "version": __version__,
                        "time": time.strftime("%d-%m-%Y", time.localtime())})

    def parsetitle(self, chunk):
        """Parse titleblock from first doc chunk, like Pandoc"""
        lines = chunk['content'].splitlines()
        if len(lines) > 3:
            if lines[0].startswith("%"):
                lines[0] = '<H1 class = "title">%s</H1>' % (lines[0].replace("%", "", ))
                if lines[1].startswith("%"):
                    lines[1] = '<strong>Author:</strong> %s <BR/>' % (lines[1].replace("%", "", ))
                if lines[2].startswith("%"):
                    lines[2] = '<strong>Date:</strong> %s <BR/>' % (lines[2].replace("%", "", ))
        chunk['content'] = "\n".join(lines)
        return chunk

    def format_docchunk(self, chunk):
        if 'number' in chunk and chunk['number'] == 1:
            chunk = self.parsetitle(chunk)

        try:
            import markdown
        except ImportError:
            message = "You'll need to install python markdown in order to use markdown to html formatter\nrun 'pip install markdown' to install"
            print(message)
            return message # was returning None, which was passed to join method
        from .markdownmath import MathExtension

        chunk["content"] = markdown.markdown(chunk["content"], extensions=[MathExtension()])
        return chunk['content']

    def formatfigure(self, chunk):
        result = ""
        figstring = ""

        for fig in chunk['figure']:
            #print(self.path + "/" + fig)
            fig_base64 = base64.b64encode(io.open(self.path + "/" + fig, "rb").read()).decode("utf-8")
            figstring += ('<img src="data:image/png;base64,%s" width="%s"/>\n' % (fig_base64, chunk['width']))

        # Figure environment
        if chunk['caption']:
            # Write labels as data-attribute for javascript etc.
            if chunk['name']:
                labelstring = 'data-label = "fig:%s"' % chunk["name"]
            else:
                labelstring = ""

            result += ("<figure>\n" \
                       "%s"
                       "<figcaption %s>%s</figcaption>\n</figure>" % (figstring, labelstring, chunk['caption']))

        else:
            result += figstring
        return result


class PwebPandocMDtoHTMLFormatter(PwebMDtoHTMLFormatter):

    def format_docchunk(self, chunk):
        if 'number' in chunk and chunk['number'] == 1:
            chunk = self.parsetitle(chunk)
        try:
            pandoc = Popen(["pandoc", "--mathjax", "-t", "html", "-f", "markdown"], stdin=PIPE, stdout=PIPE)
        except:
            sys.stderr.write("ERROR: Can't find pandoc")
            raise
        pandoc.stdin.write(chunk['content'].encode('utf-8'))
        chunk['content'] = pandoc.communicate()[0].decode('utf-8')
        return chunk['content']


class PwebPandoctoTexFormatter(PwebTexPygmentsFormatter):
    def __init__(self, source=None):
        PwebTexPygmentsFormatter.__init__(self, source)
        from pygments.formatters import LatexFormatter

        x = LatexFormatter()
        self.header = ("""\\documentclass[a4paper,11pt,final]{article}
        \\usepackage{fancyvrb, color, graphicx, hyperref, amsmath, url, textcomp}
        \\usepackage{palatino}
        \\usepackage[a4paper,text={16.5cm,25.2cm},centering]{geometry}

        %%Set different options for xetex and luatex
        \\usepackage{iftex}
        \\ifxetex\\usepackage{fontspec}\\fi

        \\ifluatex\\usepackage{fontspec}\\fi

        \\hypersetup
        {   pdfauthor = {Pweave},
            pdftitle={Published from %s},
            colorlinks=TRUE,
            linkcolor=black,
            citecolor=blue,
            urlcolor=blue
        }
        \\setlength{\parindent}{0pt}
        \\setlength{\parskip}{1.2ex}
        %% fix for pandoc 1.14
        \\providecommand{\\tightlist}{%%
            \\setlength{\\itemsep}{0pt}\\setlength{\\parskip}{0pt}}
        %s
        """) % (self.source, x.get_style_defs())
        self.footer = r"\end{document}"
        self.subheader = "\n\\begin{document}\n"

    def add_header(self):
        """Can be used to add header to self.formatted list"""
        self.formatted = self.header + self.subheader + self.formatted

    def parsetitle(self, chunk):
        """Parse titleblock from first doc chunk, like Pandoc"""
        lines = chunk['content'].splitlines()
        if len(lines) > 3:
            if lines[0].startswith("%"):
                self.header += '\n\\title{%s}\n' % (lines[0].replace("%", "", ))
                lines[0] = ""
                if lines[1].startswith("%"):
                    self.header += '\\author{%s}\n' % (lines[1].replace("%", "", ))
                    lines[1] = ""
                if lines[2].startswith("%"):
                    self.header += '\\date{%s}\n' % (lines[2].replace("%", "", ))
                    lines[2] = ""
                self.subheader += "\maketitle\n"

        chunk['content'] = "\n".join(lines)
        return chunk

    def format_docchunk(self, chunk):
        if 'number' in chunk and chunk['number'] == 1:
            chunk = self.parsetitle(chunk)
        try:
            pandoc = Popen(["pandoc", "-R", "-t", "latex", "-f", "markdown"], stdin=PIPE, stdout=PIPE)
        except:
            sys.stderr.write("ERROR: Can't find pandoc")
            raise
        pandoc.stdin.write(chunk['content'].encode('utf-8'))
        chunk['content'] = pandoc.communicate()[0].decode('utf-8')
        return chunk['content']
