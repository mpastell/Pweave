import os
import sys
import pweave
import copy
from pprint import pprint


sys.path.append('.')
os.chdir('examples')


#doc = pweave.Pweb('ma-tex.texw')
#doc.documentationmode = True
#doc.parse()
#doc.run()
#doc.format()
#doc.cachedir
#doc.write()
##doc.weave()
    
#pweave.pweave("input-test.mdw", doctype ="md2html")
#pweave.pweave("continue-test.mdw", doctype ="md2html")
pweave.pweave("AR_yw.mdw", doctype ="md2html")    
    
os.chdir('..')
