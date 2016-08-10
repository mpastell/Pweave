from . jupyter import JupyterProcessor, IPythonProcessor

class PwebProcessors(object):
    """Lists available input formats"""
    formats = {'python': {'class': IPythonProcessor,
                          'description': 'Python shell'},
               'jupyter': {'class': JupyterProcessor,
                          'description': 'Run code using Jupyter client'}}

    @classmethod
    def getprocessor(cls, kernel):
        if "python" in kernel:
            return IPythonProcessor
        else:
            return JupyterProcessor

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
        print("\nPweave supported shells:\n")
        print(cls.getformats())
        print("More info: http://mpastell.com/pweave/ \n")
