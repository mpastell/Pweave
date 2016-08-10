import nbformat


class PwebNotebookFormatter(object):

    def __init__(self, executed, *, kernel = "python3", language = "python",
                 mimetype = "text/markdown", source = None, theme = None,
                 figdir = None, wd = None):

        self.notebook = {"metadata" : {
                "kernel_info" : {
                    "name" : kernel
                },
            "language_info": {
                # if language_info is defined, its name field is required.
                "name": language
            }
        },
        "nbformat": 4,
        "nbformat_minor": 0,
        "cells": [ ]
        }

        self.execution_count = 1
        self.file_ext = "ipynb"
        self.executed = executed
        self.mimetype = mimetype

        if mimetype == "text/markdown":
            self.doc_cell_type = "markdown"
        else:
            self.doc_cell_type = "raw"

    def setexecuted(self, executed):
        self.executed = executed

    def format(self):
        for chunk in self.executed:
            if chunk["type"] == "doc":
                self.notebook["cells"].append(
                    {
                        "cell_type": self.doc_cell_type,
                        "metadata": {
                            "format" : self.mimetype
                        },
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
