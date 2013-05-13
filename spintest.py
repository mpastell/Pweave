import os
import pweave.readers
from pweave import *
from pprint import pprint
import markdown


code = \
"""
#' This is text
#+ Term=True
print(100)
x = 50
#'This is again text
#+
x = range(100)
"""

os.chdir('examples')

#x = pweave.readers.PwebSpinReader(string = code)
#x.parse()
##pprint(x.getparsed())

#Pweb.defaultoptions.update({"fig" : True})

#doc = Pweb("spincode.py")
#doc.setreader(pweave.readers.PwebSpinReader)
#doc.parse()
#doc.weave()

#doc2 = Pweb("ma.py")
#doc2.setreader(pweave.readers.PwebSpinReader)
#doc2.parse()
#doc2.weave()



#publish("FIR_design.py")
publish("IPy_test.py")
#publish('regression_whiteside.py')
#publish("FIR_design_pandoc.py")

#publish("FIR_design_pandoc.py", format = "pdf")
#publish("FIR_design_pandoc.py", format = "rst")
#os.system("pdflatex -shell-escape FIR_design_pandoc.tex")

#publish("FIR_design_pandoc.py", format = "pandoc2html")

#spin("FIR_design_pandoc.py")
#convert("FIR_design.py", informat="script", outformat="noweb", pandoc_args="-t latex")
#convert("regression_whiteside.py", informat="script", outformat="script", pandoc_args="-t latex")
#pweave("FIR_design.Pnw", doctype ="texpygments") 
