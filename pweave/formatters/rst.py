from .base import PwebFormatter


class PwebRstFormatter(PwebFormatter):
    def initformat(self):
        self.formatdict = dict(
            codestart=".. code:: %s\n\n",
            codeend="\n",
            outputstart=".. code::\n\n",
            outputend="\n",
            # rst has specific format (doctest) for term blocks
            termstart=".. code:: %s\n\n",
            termend="\n",
            termindent="    ",
            termprompt=">>> ",
            termcont="... ",
            indent="    ",
            figfmt=".png",
            extension="rst",
            width="15 cm",
            doctype="rst",
        )
        self.fig_mimetypes = ["image/png", "image/jpg"]
        self.mimetypes = ["text/restructuredtext"]
        self.file_ext = "rst"

    def formatfigure(self, chunk):
        fignames = chunk["figure"]
        caption = chunk["caption"]
        width = chunk["width"]
        result = ""
        figstring = ""

        for fig in fignames:
            figstring += "\n\n.. image:: %s\n   :width: %s\n\n" % (fig, width)

        if chunk["caption"]:
            result += (
                "\n\n.. figure:: %s\n"
                "   :width: %s\n\n"
                "   %s\n\n" % (fignames[0], width, caption)
            )
        else:
            result += figstring

        return result

    def add_prompts(self, text):
        """Add prompts to the text"""
        lines = []
        in_code = False
        in_continuation = False

        for line in text.split("\n"):
            if line or in_code:
                in_code = True

                if line.startswith(" "):
                    line = self.formatdict["termcont"] + line
                    in_continuation = True
                else:
                    if in_continuation:
                        line = self.formatdict["termcont"] + line
                    else:
                        line = self.formatdict["termprompt"] + line
                    in_continuation = False

            lines.append(line)

        text = "\n".join(lines)

        if text.endswith(self.formatdict["termprompt"]):
            text = text[:-4]

        return text

    def _indent(self, text):
        """Indent blocks for formats where indent is significant"""
        if not text.startswith("\n"):
            text = "\n" + text
            return text.replace("\n", "\n" + self.formatdict["indent"])[1:]

        return text.replace("\n", "\n" + self.formatdict["indent"])

    def _termindent(self, text):
        return text.replace("\n", "\n" + self.formatdict["termindent"])


class PwebSphinxFormatter(PwebRstFormatter):
    def initformat(self):
        self.formatdict = dict(
            codestart=".. code-block:: %s\n\n",
            codeend="\n",
            outputstart="::\n\n",
            outputend="\n\n",
            # rst has specific format (doctest) for term blocks
            termstart=".. code-block:: %s\n",
            termend="\n",
            termindent="    ",
            termprompt=">>> ",
            termcont="... ",
            indent="    ",
            # Sphinx determines the figure format automatically
            # for different output formats
            figfmt=".*",
            savedformats=[".png", ".pdf"],
            extension="rst",
            width="15 cm",
            doctype="rst",
        )
        self.fig_mimetypes = ["image/png", "image/jpg"]
        self.mimetypes = ["text/restructuredtext"]
        self.file_ext = "rst"

    def formatfigure(self, chunk):
        fignames = chunk["figure"]
        caption = chunk["caption"]
        width = chunk["width"]
        result = ""
        figstring = ""

        for fig in fignames:
            figstring += "\n\n.. image:: %s\n   :width: %s\n\n" % (fig, width)

        if chunk["caption"]:
            result += (
                "\n\n.. figure:: %s\n"
                "   :width: %s\n\n"
                "   %s\n\n" % (fignames[0], width, caption)
            )
        else:
            result += figstring

        return result
