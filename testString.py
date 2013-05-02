import os
import sys
from pweave import *
import copy
from pprint import pprint


sys.path.append('.')

doc = Pweb("")
doc.parse(string = "Hello\n<<>>=\nprint(100)\n@\nBye!\n")
print doc.parsed  

os.chdir('examples/')
stitch("ma.py")
os.chdir('..')

    
    

