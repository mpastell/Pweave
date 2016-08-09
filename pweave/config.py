
rcParams = {"figdir": "figures",
            "usematplotlib": True,
            "storeresults": False,
            "cachedir": 'cache',
            "shell_path": "python",
            "chunk": {"defaultoptions": {
                "echo": True,
                "results": 'verbatim',
                "fig": True,
                "include": True,
                "evaluate": True,
                "caption": False,
                "term": False,
                "name": None,
                "wrap": True,
                "f_pos": "htpb",
                "f_size": (6, 4),
                "f_env": None,
                "dpi" : 100,
                "f_spines": True,
                "complete": True,
                "engine": "python",
                "option_string": "",
                "display_data" : True,
                "display_stream" : True
            }
    }
}

class PwebProcessorGlobals(object):
    """A class to hold the globals used in processors"""
    globals = {}