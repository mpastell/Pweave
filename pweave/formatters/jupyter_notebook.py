import nbformat


class PwebNotebookFormatter(object):

    def __init__(self, doc):
        self.notebook = {"metadata" : {
                "kernel_info" : {
                    "name" : doc.kernel
                },
            "language_info": {
                # if language_info is defined, its name field is required.
                "name": doc.language
            }
        },
        "nbformat": 4,
        "nbformat_minor": 0,
        "cells": [
                # list of cell dictionaries, see below
            ]
        }
        self.execution_count = 1
        self.formatdict = {"extension" : "ipynb"}


    def setexecuted(self, executed):
        self.executed = executed

    def format(self):
        for chunk in self.executed:
            if chunk["type"] == "doc":
                self.notebook["cells"].append(
                    {
                        "cell_type": "markdown",
                        "metadata": {},
                        "source": chunk["content"],
                    }
                )
            if chunk["type"] == "code":
                self.notebook["cells"].append(
                    {
                        "cell_type": "code",
                        "execution_count" : self.execution_count,
                        "metadata": {
                            "collapsed": False,
                            "autoscroll": "auto",
                            "options" : chunk["options"]
                        },
                        "source": chunk["content"].lstrip(),
                        "outputs" : chunk["result"]
                    }
                )
                self.execution_count +=1
        self.notebook = nbformat.from_dict(self.notebook)

    def getformatted(self):
        return nbformat.writes(self.notebook)

    def getformatdict(self):
        return self.formatdict
