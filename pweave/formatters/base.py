import sys

if sys.version_info.major == 2:
    from ._Python2.base import *

else:
    from ._Python3.base import *