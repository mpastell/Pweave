import sys

if sys.version_info.major == 2:
    from ._Python2.jupyter_notebook import *

else:
    from ._Python3.jupyter_notebook import *