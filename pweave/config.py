
rcParams = {"figdir": "figures",
            "usematplotlib": True,
            "storeresults": False,
            "cachedir": 'cache',
            "chunk": {"defaultoptions": {
                "echo": True,
                "results": 'verbatim',
                "fig": True,
                "include": True,
                "evaluate": True,
                "caption": False,
                "term": False,
                "name": None,
                "wrap": "output",
                "f_pos": "htpb",
                "f_size": (6, 4),
                "f_env": None,
                "dpi" : 100,
                "f_spines": True,
                "complete": True,
                "option_string": "",
                "display_data" : True,
                "display_stream" : True
            }
    }
}

class PwebProcessorGlobals(object):
    """A class to hold the globals used in processors"""
    globals = {}