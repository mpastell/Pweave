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
