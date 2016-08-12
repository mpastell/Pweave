from .base import PwebFormatter
from nbconvert import filters

class PwebTexFormatter(PwebFormatter):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mimetypes = ["text/latex"]
        self.fig_mimetypes = ["application/pdf", "image/png", "image/jpg"]
        self.file_ext = "tex"

    def initformat(self):
        self.formatdict = dict(codestart='\\begin{verbatim}',
                               codeend='\end{verbatim}\n',
                               outputstart='\\begin{verbatim}',
                               outputend='\end{verbatim}\n',
                               figfmt='.pdf',
                               width='\\linewidth',
                               doctype='tex')

    def formatfigure(self, chunk):
        fignames = chunk['figure']
        caption = chunk['caption']
        width = chunk['width']
        result = ""
        figstring = ""

        if chunk["f_env"] is not None:
            result += "\\begin{%s}\n" % chunk["f_env"]

        for fig in fignames:
            figstring += ("\\includegraphics[width= %s]{%s}\n" % (width, fig))

        # Figure environment
        if chunk['caption']:
            result += ("\\begin{figure}[%s]\n"
                       "\\center\n"
                       "%s"
                       "\\caption{%s}\n" % (chunk['f_pos'], figstring, caption))
            if 'name' in chunk:
                result += "\label{fig:%s}\n" % chunk['name']
            result += "\\end{figure}\n"

        else:
            result += figstring

        if chunk["f_env"] is not None:
            result += "\\end{%s}\n" % chunk["f_env"]

        return result


class PwebMintedFormatter(PwebTexFormatter):
    def initformat(self):
        self.formatdict = dict(
            codestart=r'\begin{minted}[mathescape, fontsize=\small, xleftmargin=0.5em]{%s}',
            codeend='\end{minted}\n',
            outputstart=r'\begin{minted}[fontsize=\small, xleftmargin=0.5em, mathescape, frame = leftline]{text}',
            outputend='\end{minted}\n',
            termstart=r'\begin{minted}[fontsize=\footnotesize, xleftmargin=0.5em, mathescape]{%s}',
            termend='\end{minted}\n',
            figfmt='.pdf',
            extension='tex',
            width='\\linewidth',
            doctype='tex')
        self.file_ext = "tex"
        self.fig_mimetypes = ["application/pdf", "image/png", "image/jpg"]


class PwebTexPygmentsFormatter(PwebTexFormatter):
    def initformat(self):

        self.formatdict = dict(
            codestart="",
            codeend="",
            outputstart = "\n" + r"\begin{Verbatim}[commandchars=\\\{\},frame=leftline,fontsize=\small, xleftmargin=0.5em]",
            outputend = r"\end{Verbatim}" +"\n",
            #termstart= "\n" + r"\begin{Verbatim}[commandchars=\\\{\},frame=single,fontsize=\small, xleftmargin=0.5em]",
            #termend= r"\end{Verbatim}" +"\n",
            figfmt='.pdf',
            extension='tex',
            width='\\linewidth',
            doctype='tex')
        self.file_ext = "tex"
        self.fig_mimetypes = ["application/pdf", "image/png", "image/jpg"]

    def highlight_ansi_and_escape(self, text):
        return filters.ansi2latex(text)

    def format_codechunks(self, chunk):
        from pygments import highlight
        from IPython.lib.lexers import IPyLexer
        #from pygments.lexers import PythonLexer, TextLexer, PythonConsoleLexer
        from pygments.formatters import LatexFormatter

        chunk['content'] = highlight(chunk['content'], IPyLexer(),
                                     LatexFormatter(verboptions="frame=single,fontsize=\small, xleftmargin=0.5em"))
        return PwebFormatter.format_codechunks(self, chunk)


class PwebTexPweaveFormatter(PwebTexFormatter):
    """User defined formatting for chunks in header using pweavecode, pweaveoutput and pweaveterm environments"""

    def initformat(self):
        self.formatdict = dict(
            codestart=r'\begin{pweavecode}',
            codeend='\end{pweavecode}\n',
            outputstart=r'\begin{pweaveout}',
            outputend='\end{pweaveout}\n',
            termstart=r'\begin{pweaveterm}',
            termend='\end{pweaveterm}\n',
            figfmt='.pdf',
            extension='tex',
            width='\\linewidth',
            doctype='tex')
        self.file_ext = "tex"
