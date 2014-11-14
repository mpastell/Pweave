#Moved globals from Pweb, check to see after move each for invalid references!


rcParams = {"figdir" : "figures",
            "usematplotlib" : True,
            "storeresults" : False,
            "cachedir" : 'cache',
            "chunk" : {"defaultoptions" : {
                "echo" : True,
                "results" : 'verbatim',
                "fig" : True,
                "include" : True,
                "evaluate" : True,
                "caption" : False,
                "term" : False,
                "name" : None,
                "wrap" : True,
                "f_pos" : "htpb",
                "f_size" : (8, 6),
                "f_env" : None,
                "f_spines" : True,
                "complete" : True,
                "engine" : "python",
                "option_string" : ""
                }
            }
    }

class PwebProcessorGlobals(object):
    """A class to hold the globals used in processors"""
    globals = {}