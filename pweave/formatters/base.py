import base64
import copy
import os
import re
import textwrap

from nbconvert import filters


# Pweave output formatters
class PwebFormatter(object):
    """Base class for all not-notebook formatters"""

    def __init__(
        self,
        executed,
        *,
        kernel="python3",
        language="python",
        mimetype=None,
        source=None,
        theme=None,
        figdir="figures",
        wd="."
    ):

        self.mimetypes = []  # other supported mimetypes than text/plain
        self.executed = executed
        self.figdir = figdir
        self.wd = wd
        self.source = source
        self.theme = theme
        self.language = language
        self.exceptions = []

        # To be set in child classess
        self.file_ext = None
        self.header = None
        self.footer = None

        self.wrapper = textwrap.TextWrapper(
            subsequent_indent="", break_long_words=False
        )

        self.mime_extensions = {
            "application/pdf": "pdf",
            "image/png": "png",
            "image/jpg": "jpg",
        }
        self.initformat()
        self._fillformatdict()

    def initformat(self):
        pass

    def format(self):
        self.formatted = []

        for chunk in self.executed:
            # Fill in options for code chunks
            if chunk["type"] == "code":
                for key in self.formatdict.keys():
                    if key not in chunk:
                        chunk[key] = self.formatdict[key]

            # Wrap text if option is set
            if chunk["type"] == "code":
                if chunk["wrap"] is True or chunk["wrap"] == "code":
                    chunk["content"] = self._wrap(chunk["content"])

            # Preformat chunk content before default formatters
            chunk = self.preformat_chunk(chunk)

            if chunk["type"] == "doc":
                self.formatted.append(self.format_docchunk(chunk))
            elif chunk["type"] == "code":
                self.formatted.append(self.format_codechunks(chunk))
            else:
                self.formatted.append(chunk["content"])

        self.formatted = "\n".join(self.formatted)
        self.convert()  # Convert to e.g. markdown
        self.add_header()
        self.add_footer()

    def convert(self):
        pass

    def preformat_chunk(self, chunk):
        """You can use this method in subclasses to preformat chunk content"""
        return chunk

    def figures_from_chunk(self, chunk):
        # For backwards compatibility, only process final figure
        if not chunk["multi_fig"] and not chunk["complete"]:
            return []

        """Extract base64 encoded figures from chunk"""
        figs = []
        i = 1

        for out in chunk["result"]:
            if out["output_type"] != "display_data":
                continue

            # Loop trough mimetypes in order of preference
            for mimetype in self.fig_mimetypes:
                if mimetype in out["data"]:
                    fig_name, include_name = self.get_figname(chunk, i, mimetype)
                    figs.append(include_name)
                    bfig = base64.b64decode(out["data"][mimetype])
                    f = open(fig_name, "wb")
                    f.write(bfig)
                    f.close()
                    i += 1
                    break

        # print(figs)
        return figs

    def format_termchunk(self, chunk):
        if chunk["echo"] and chunk["results"] != "hidden":
            chunk["result"] = self._termindent(chunk["result"])
            result = "%(termstart)s%(result)s%(termend)s" % chunk
        else:
            result = ""

        return result

    def format_codeblock(self, chunk):
        pass

    def format_results(self, chunk):
        pass

    def render_jupyter_output(self, out, chunk):
        if out["output_type"] == "error":
            if not chunk["allow_exceptions"]:
                ansi_escape = re.compile(r"(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]")
                lines = []

                for line in out["traceback"]:
                    lines.append(ansi_escape.sub("", line))

                self.exceptions.append("\n".join(lines))

            return self.render_traceback("".join(out["traceback"]), chunk)

        if out["output_type"] == "stream":
            return self.render_text(out["text"], chunk)

        for mimetype in self.mimetypes:
            if mimetype in out["data"]:
                if mimetype == "application/javascript":
                    return "\n<script>" + out["data"][mimetype] + "</script>"
                else:
                    return "\n" + out["data"][mimetype]

        # Return nothing if data is shown as figure
        for mimetype in self.fig_mimetypes:
            if mimetype in out["data"]:
                return ""

        if "text/plain" in out["data"]:
            return self.render_text(out["data"]["text/plain"], chunk)
        else:
            return ""

    def highlight_ansi_and_escape(self, text):
        return self.escape(filters.strip_ansi(text))

    def escape(self, text):
        return text

    def render_traceback(self, text, chunk):
        chunk = copy.deepcopy(chunk)
        text = self.highlight_ansi_and_escape(text)
        return self.format_text_result(text, chunk)

    def render_text(self, text, chunk):
        chunk = copy.deepcopy(chunk)
        text = self.highlight_ansi_and_escape(text)
        return self.format_text_result(text, chunk)

        # Set lexers for code and output

    def format_text_result(self, text, chunk):
        chunk["result"] = text
        result = ""

        if "%s" in chunk["outputstart"]:
            chunk["outputstart"] = chunk["outputstart"] % self.language

        if "%s" in chunk["termstart"]:
            chunk["termstart"] = chunk["termstart"] % self.language

        # Other things than term
        if chunk["results"] == "verbatim":
            if len(chunk["result"].strip()) > 0:
                if (
                    chunk["wrap"] is True
                    or chunk["wrap"] == "results"
                    or chunk["wrap"] == "output"
                ):
                    chunk["result"] = self._wrap(chunk["result"])
                chunk["result"] = "%s\n" % chunk["result"].rstrip()
                chunk["result"] = self._indent(chunk["result"])
                result += "%(outputstart)s%(result)s%(outputend)s" % chunk
        elif chunk["results"] != "verbatim":
            result += self.fix_linefeeds(text)

        return result

    def fix_linefeeds(self, text):
        """Add empty line to start and end of string if it
        they don't exist"""

        if not text.startswith("\n"):
            text = "\n" + text

        if not text.endswith("\n"):
            text = text + "\n"

        return text

    def format_codechunks(self, chunk):
        # Code is not executed
        if not chunk["evaluate"]:
            chunk["content"] = self._indent(chunk["content"])
            chunk["content"] = self.fix_linefeeds(chunk["content"])

            if chunk["echo"]:
                if chunk["chunk_type"] == "output":
                    if "%s" in chunk["outputstart"]:
                        chunk["outputstart"] = chunk["outputstart"] % self.language
                    result = "%(outputstart)s%(content)s%(outputend)s" % chunk
                else:
                    if "%s" in chunk["codestart"]:
                        chunk["codestart"] = chunk["codestart"] % self.language
                    result = "%(codestart)s%(content)s%(codeend)s" % chunk

                return result
            else:
                return ""

        # Code is executed
        # -------------------
        if "%s" in chunk["codestart"]:
            chunk["codestart"] = chunk["codestart"] % self.language

        result = ""

        if chunk["echo"]:
            if chunk["term_prompts"]:
                chunk["content"] = self.add_prompts(chunk["content"])

            chunk["content"] = self._indent(chunk["content"])
            chunk["content"] = self.fix_linefeeds(chunk["content"])
            result += "%(codestart)s%(content)s%(codeend)s" % chunk

        if chunk["results"] != "hidden":
            stream_result = {"output_type": "stream", "text": ""}
            other_result = ""

            for out in chunk["result"]:
                if out["output_type"] == "stream":
                    stream_result["text"] += out["text"]
                elif out["output_type"] == "execute_result":
                    other_result += self.render_jupyter_output(out, chunk)
                elif out["output_type"] == "error":
                    other_result += self.render_jupyter_output(out, chunk)

            result += self.render_jupyter_output(stream_result, chunk)
            result += other_result

        # Handle figures
        chunk["figure"] = self.figures_from_chunk(
            chunk
        )  # Save embedded figures to file

        if chunk["fig"] and chunk["figure"]:
            if chunk["include"]:
                result += self.formatfigure(chunk)

        return result

    def format_docchunk(self, chunk):
        return chunk["content"]

    def formatfigure(chunk):
        return ""

    def add_prompts(content):
        return content

    def add_header(self):
        """Can be used to add header to self.formatted list"""
        if self.header is not None:
            self.formatted = self.header + self.formatted

    def add_footer(self):
        """Can be used to add footer to self.formatted list"""
        if self.footer is not None:
            self.formatted += self.footer

    def getformatdict(self):
        return self.formatdict

    def getformatted(self):
        return self.formatted

    def updateformatdict(self, format_dict):
        self.formatdict.update(format_dict)

    def _wrapper(self, string, width=80):
        """Wrap a string to specified width like Python terminal"""
        if len(string) < width:
            return string

        # Wrap also comment lines
        if string.lstrip()[0] == "#":
            return (
                string[0:width]
                + "\n"
                + self._wrapper("#" + string[width : len(string)], width)
            )
        else:
            return (
                string[0:width]
                + "\n"
                + self._wrapper(string[width : len(string)], width)
            )

    def _wrap(self, content):
        splitted = content.split("\n")
        result = ""

        for line in splitted:
            result += self.wrapper.fill(line) + "\n"

        return result

    def _fillformatdict(self):
        """Fill in the blank options that are now only used for rst
        but also allow e.g. special latex style for terminal blocks etc."""
        self._fillkey("termstart", self.formatdict["codestart"])
        self._fillkey("termend", self.formatdict["codeend"])
        self._fillkey("savedformats", list([self.formatdict["figfmt"]]))

    def _fillkey(self, key, value):
        if key not in self.formatdict:
            self.formatdict[key] = value

    def _indent(self, text):
        """Indent blocks for formats where indent is significant"""
        return text
        # return(text.replace('\n', '\n' + self.formatdict['indent']))

    def _termindent(self, text):
        """Indent blocks for formats where indent is significant"""
        return text
        # return(text.replace('\n', '\n' + self.formatdict['termindent']))

    def sanitize_filename(self, fname):
        return "".join(i for i in fname if i not in "\/:*?<>|")

    def get_figname(self, chunk, i, mimetype):
        save_dir = self.getFigDirectory()
        include_dir = self.figdir

        ext = "." + self.mime_extensions[mimetype]
        base = os.path.splitext(os.path.basename(self.source))[0]

        if chunk["name"] is None:
            prefix = base + "_figure" + str(chunk["number"]) + "_" + str(i)
        else:
            prefix = base + "_" + self.sanitize_filename(chunk["name"]) + "_" + str(i)

        self.ensureDirectoryExists(self.getFigDirectory())

        save_name = os.path.join(save_dir, prefix + ext)
        include_name = os.path.join(include_dir, prefix + ext).replace("\\", "/")

        return save_name, include_name

    def getFigDirectory(self):
        return os.path.join(self.wd, self.figdir)

    def ensureDirectoryExists(self, figdir):
        if not os.path.isdir(figdir):
            os.mkdir(figdir)
