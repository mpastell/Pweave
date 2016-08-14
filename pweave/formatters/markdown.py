from .base import PwebFormatter
import sys

class PwebPandocFormatter(PwebFormatter):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.file_ext = "md"
        self.mimetypes = ["text/markdown"]
        self.fig_mimetypes = ["image/png", "image/jpg", "application/svg+xml"]


    def initformat(self):
        self.formatdict = dict(codestart='```%s',
                               codeend='```\n\n',
                               outputstart='```',
                               outputend='```\n\n',
                               indent='',
                               termindent='',
                               figfmt='.png',
                               extension='md',
                               width = None,
                               doctype='pandoc')

    def make_figure_string(self, figname, width, label, caption = ""):
        figstring = "![%s](%s)" % (caption, figname)

        #Pandoc >= 1.16 supports figure width and id

        attributes = ""
        if label is not None:
            attributes += "#%s " % label
        if width is not None:
            attributes += "width=%s" % width
        if attributes != "":
            figstring += "{%s}" % attributes

        if caption == "":
            figstring += "\\"

        figstring += "\n"

        return figstring

    def formatfigure(self, chunk):

        fignames = chunk['figure']

        if chunk["caption"]:
            caption = chunk["caption"]
        else:
            caption = ""

        figstring = ""

        if chunk['caption'] and len(fignames) > 0:
            if len(fignames) > 1:
                print("INFO: Only including the first plot in a chunk when the caption is set")
            figstring = self.make_figure_string(fignames[0], chunk["width"], chunk["name"], caption)
            return figstring

        for fig in fignames:
            figstring += self.make_figure_string(fig, chunk["width"], chunk["name"])

        return figstring


class PwebLeanpubFormatter(PwebFormatter):
    def initformat(self):
        self.formatdict = dict(codestart='{line-numbers=off}\n~~~~~~~~',
                               codeend='~~~~~~~~\n\n',
                               outputstart='{line-numbers=off}\n~~~~~~~~',
                               outputend='~~~~~~~~\n\n',
                               indent='',
                               termindent='',
                               figfmt='.png',
                               extension='txt',
                               width='15 cm',
                               doctype='leanpub')
        self.file_ext = "md"
        self.mimetypes = ["text/markdown"]
        self.fig_mimetypes = ["image/png", "image/jpg", "application/svg+xml"]


    def formatfigure(self, chunk):
        fignames = chunk['figure']
        caption = chunk['caption']
        width = chunk['width']
        result = ""
        figstring = ""

        # print chunk["name"]

        if chunk['caption']:
            if fignames:
                result += '![%s](%s)\n' % (caption, fignames[0])
                if len(fignames) > 1:
                    for fig in fignames[1:]:
                        figstring += '![](%s)\n' % fig
                        sys.stderr.write("Warning, only the first figure gets a caption\n")
        else:
            for fig in fignames:
                figstring += '![](%s)\n' % fig
            result += figstring
        return result


class PwebSoftCoverFormatter(PwebLeanpubFormatter):
    def initformat(self):
        self.formatdict = dict(codestart='\n```python',
                               codeend='```\n\n',
                               outputstart='```\n',
                               outputend='```\n\n',
                               indent='',
                               termindent='',
                               figfmt='.png',
                               extension='md',
                               width='15cm',
                               doctype='softcover')
        self.file_ext = "md"
        self.mimetypes = ["text/markdown"]
        self.fig_mimetypes = ["image/png", "image/jpg", "application/svg+xml"]

    def formatfigure(self, chunk):
        fignames = chunk['figure']
        caption = chunk['caption']
        width = chunk['width']
        label = chunk['name']
        result = ""
        figstring = ""

        if chunk['caption']:
            if fignames:
                result += '![%s \\label{fig:%s}](%s)\n' % (caption, label, fignames[0])
                if len(fignames) > 1:
                    for fig in fignames[1:]:
                        figstring += '![](%s)\n' % fig
                        sys.stderr.write("Warning, only the first figure gets a caption\n")
        else:
            for fig in fignames:
                figstring += '![](%s)\n' % fig
            result += figstring
        return result

