import sys

if sys.version_info.major == 2:
    from ._frameworkForTests_Python2 import *

else:
    from ._frameworkForTests_Python3 import *