
from . pythonprocessor import PwebProcessor

class PwebProcessors(object):
    """Lists available input formats"""
    formats = {'python': {'class': PwebProcessor,
                          'description': 'Python shell'}}
               #,
               #'ipython': {'class': PwebIPythonProcessor,
               #            'description': 'IPython shell'},
               #'epython': {'class': PwebSubProcessor,
               #            'description': 'Python as separate process'},
               #'octave': {'class': OctaveProcessor,
               #           'description': 'Run code using Octave'},
               #'matlab': {'class': MatlabProcessor,
               #           'description': 'Run code using Matlab'},
               #'jupyter': {'class': JupyterProcessor,
               #           'description': 'Run code using Jupyter client'}}

    @classmethod
    def getProcessor(cls, shell):
        return cls.formats[shell]['class']

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
