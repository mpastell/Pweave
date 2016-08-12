import os
import sys

class MimeType(object):
    """Default mimetypes for input extensions"""

    def __init__(self, mimetype, file_ext):
        self.type = mimetype
        self.file_ext = file_ext



class MimeTypes(object):
    """Methods for handling mimetypes and file extensions"""

    # Supported input types
    known_types = [
            ("text/markdown", "md"),
            ("text/latex", "tex"),
            ("text/html", "html"),
            ("text/restructuredtext", "rst"),
    ]

    @classmethod
    def guess_mimetype(cls, filename):
        """Guess mimetype based on input filename"""
        _, ext = os.path.splitext(filename)
        ext = ext.lower()

        for type in cls.known_types:
            if type[1] in ext:
                return MimeType(*type)

        #Default to markdown
        return MimeType("text/markdown", "md")

    @classmethod
    def get_mimetype(cls, mimetype):
        """Return mimetype object based on type"""

        for type in cls.known_types:
            if type[0] == mimetype:
                return MimeType(*type)

        sys.stderr.write("Unsupport mimetype, using markdown")
        return MimeType("text/markdown", "md")
