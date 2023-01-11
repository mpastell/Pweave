rcParams = {
    "cachedir": "cache",
    "figdir": "figures",
    "storeresults": False,
    "usematplotlib": True,
    "chunk": {
        "defaultoptions": {
            "caption": False,
            "chunk_type": "code",
            "complete": True,
            "display_data": True,
            "display_stream": True,
            "dpi": 200,
            "echo": True,
            "evaluate": True,
            "f_env": None,
            "f_pos": "htpb",
            "f_size": (6, 4),
            "f_spines": True,
            "fig": True,
            "include": True,
            "multi_fig": True,
            "name": None,
            "option_string": "",
            "results": "verbatim",
            "term_prompts": False,
            "term": False,
            "wrap": "output",
        }
    },
}


class PwebProcessorGlobals(object):
    """A class to hold the globals used in processors"""

    globals = {}
