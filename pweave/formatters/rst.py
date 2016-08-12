from .base import PwebFormatter

class PwebRstFormatter(PwebFormatter):
    def initformat(self):
        self.formatdict = dict(codestart='.. code:: %s\n',
                               codeend='\n\n',
                               outputstart='.. code::\n',
                               outputend='\n\n',
                               # rst has specific format (doctest) for term blocks
                               termstart='.. code:: %s\n',
                               termend='\n\n',
                               termindent='    ',
                               indent='    ',
                               figfmt='.png',
                               extension='rst',
                               width='15 cm',
                               doctype='rst')
        self.fig_mimetypes = ["image/png", "image/jpg"]
        self.mimetypes = ["text/restructuredtext"]
        self.file_ext = "rst"

    def formatfigure(self, chunk):
        fignames = chunk['figure']
        caption = chunk['caption']
        width = chunk['width']
        result = ""
        figstring = ""

        for fig in fignames:
            figstring += ('.. image:: %s\n   :width: %s\n\n' % (fig, width))

        if chunk['caption']:
            result += (".. figure:: %s\n"
                       "   :width: %s\n\n"
                       "   %s\n\n" % (fignames[0], width, caption))
        else:
            result += figstring
        return result



    def _indent(self, text):
        """Indent blocks for formats where indent is significant"""
        if not text.startswith("\n"):
            text = "\n" + text
        return text.replace('\n', '\n' + self.formatdict['indent'])

    def _termindent(self, text):
        return text.replace('\n', '\n' + self.formatdict['termindent'])

class PwebSphinxFormatter(PwebRstFormatter):
    def initformat(self):
        self.formatdict = dict(codestart='.. code-block:: %s\n',
                               codeend='\n\n',
                               outputstart='::\n',
                               outputend='\n\n',
                               # rst has specific format (doctest) for term blocks
                               termstart='.. code-block:: %s\n',
                               termend='\n\n',
                               termindent='    ',
                               indent='    ',
                               # Sphinx determines the figure format automatically
                               # for different output formats
                               figfmt='.*',
                               savedformats=['.png', '.pdf'],
                               extension='rst',
                               width='15 cm',
                               doctype='rst')
        self.fig_mimetypes = ["image/png", "image/jpg"]
        self.mimetypes = ["text/restructuredtext"]
        self.file_ext = "rst"

    def formatfigure(self, chunk):
        fignames = chunk['figure']
        caption = chunk['caption']
        width = chunk['width']
        result = ""
        figstring = ""

        for fig in fignames:
            figstring += ('.. image:: %s\n   :width: %s\n\n' % (fig, width))

        if chunk['caption']:
            result += (".. figure:: %s\n" \
                       "   :width: %s\n\n" \
                       "   %s\n\n" % (fignames[0], width, caption))
        else:
            result += figstring
        return result
