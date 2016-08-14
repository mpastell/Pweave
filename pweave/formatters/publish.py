from .base import PwebFormatter
from .tex import PwebTexPygmentsFormatter
from subprocess import Popen, PIPE
import base64
import sys
import os
import io
import html
from nbconvert import filters

class PwebHTMLFormatter(PwebFormatter):


    def preformat_chunk(self, chunk):
        if chunk["type"] == "doc":
            return chunk

        from pygments import highlight
        from IPython.lib.lexers import IPyLexer
        #from pygments.lexers import PythonLexer, PythonConsoleLexer, TextLexer
        from pygments.formatters import HtmlFormatter

        chunk['content'] = highlight(chunk['content'], IPyLexer(), HtmlFormatter())
        return chunk

    def initformat(self):
        self.formatdict = dict(codestart='',
                               codeend='',
                               outputstart='\n<div class="highlight"><pre>',
                               outputend='</pre></div>\n',
                               figfmt='.png',
                               width='600',
                               doctype='html')

        self.fig_mimetypes = ["application/svg+xml", "image/png", "image/jpg"]
        self.mimetypes = ["text/html", "application/javascript"]
        self.file_ext = "html"


    def escape(self, text):

        return html.escape(text)

    def highlight_ansi_and_escape(self, text):
        return filters.ansi2html(text)

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        from .templates import htmltemplate
        from .. import themes
        from pygments.formatters import HtmlFormatter
        from .. import __version__
        import time

        self.mimetypes = ["text/html", "text/markdown", "application/javascript"]

        theme_css = ""
        try:
            theme_css += getattr(themes, self.theme)
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
            fh = open(os.path.join(self.wd, fig), "rb")
            bfig = fh.read()
            fh.close()
            fig_base64 = base64.b64encode(bfig).decode("utf-8")
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


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from pygments.formatters import LatexFormatter

        self.header = ("""\\documentclass[a4paper,11pt,final]{article}
        \\usepackage{fancyvrb, color, graphicx, hyperref, amsmath, url, textcomp}
        \\usepackage{palatino}
        \\usepackage[a4paper,text={16.5cm,25.2cm},centering]{geometry}

        %%Set different options for xetex and luatex
        \\usepackage{iftex}
        \\ifxetex\\usepackage{fontspec}\\fi

        \\ifluatex\\usepackage{fontspec}\\fi

        \\usepackage{xcolor}
        %% ANSI colors from nbconvert
        \\definecolor{ansi-black}{HTML}{3E424D}
        \\definecolor{ansi-black-intense}{HTML}{282C36}
        \\definecolor{ansi-red}{HTML}{E75C58}
        \\definecolor{ansi-red-intense}{HTML}{B22B31}
        \\definecolor{ansi-green}{HTML}{00A250}
        \\definecolor{ansi-green-intense}{HTML}{007427}
        \\definecolor{ansi-yellow}{HTML}{DDB62B}
        \\definecolor{ansi-yellow-intense}{HTML}{B27D12}
        \\definecolor{ansi-blue}{HTML}{208FFB}
        \\definecolor{ansi-blue-intense}{HTML}{0065CA}
        \\definecolor{ansi-magenta}{HTML}{D160C4}
        \\definecolor{ansi-magenta-intense}{HTML}{A03196}
        \\definecolor{ansi-cyan}{HTML}{60C6C8}
        \\definecolor{ansi-cyan-intense}{HTML}{258F8F}
        \\definecolor{ansi-white}{HTML}{C5C1B4}
         \\definecolor{ansi-white-intense}{HTML}{A1A6B2}

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
        """) % (self.source, LatexFormatter().get_style_defs())
        self.footer = r"\end{document}"
        self.subheader = "\n\\begin{document}\n"
        self.fig_mimetypes = ["application/pdf", "image/png", "image/jpg"]

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
