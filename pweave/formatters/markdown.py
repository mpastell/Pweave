from .base import PwebFormatter
from distutils.version import LooseVersion
from subprocess import Popen, PIPE
import sys

class PwebPandocFormatter(PwebFormatter):

    def __init__(self, source=None):
        PwebFormatter.__init__(self, source)
        pandoc_ver = False

        try:
            pandoc = Popen(["pandoc", "--version"], stdin=PIPE, stdout=PIPE)
            pandoc_ver = pandoc.communicate()[0].decode('utf-8').split("\n")[0]
            pandoc_ver = LooseVersion(pandoc_ver.split(" ")[1])
        except:
            pandoc_ver = LooseVersion("0.0.1")
            print("Error in trying to detect pandoc version")

        if pandoc_ver < LooseVersion("1.16.0"):
            self.new_pandoc = False
            print("Your pandoc version is below 1.16, not setting figure size and id")
        else:
            self.new_pandoc = True

    def initformat(self):
        self.formatdict = dict(codestart='~~~~{.%s}',
                               codeend='~~~~~~~~~~~~~\n\n',
                               outputstart='~~~~{.%s}',
                               outputend='~~~~~~~~~~~~~\n\n',
                               indent='',
                               termindent='',
                               figfmt='.png',
                               extension='md',
                               width = None,
                               doctype='pandoc')

    def make_figure_string(self, figname, width, label, caption = ""):
        figstring = "![%s](%s)" % (caption, figname)

        #Pandoc >= 1.16 supports figure width and id
        if (self.new_pandoc):
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
            figstring += self.make_figure_string(fignames[0], chunk["width"], chunk["name"])

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

