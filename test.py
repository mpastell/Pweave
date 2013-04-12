import os
import sys
import pweave
import markdown
import copy
from pprint import pprint


sys.path.append('.')
os.chdir('examples')


class MyTex(pweave.PwebTexFormatter):
    
    before_format = []

    def preformat_chunk(self, chunk):
        if chunk['type'] == 'doc':
            return(chunk)
        
        chunk['content'] = highlight(chunk['content'], PythonLexer(), LatexFormatter())
        return(chunk)

    def initformat(self):
        self.formatdict = dict(codestart = '',
                codeend = '',
                outputstart = '\\begin{verbatim}',
                outputend = '\end{verbatim}\n',
                figfmt = '.pdf',
                extension = 'tex',
                width = '\\textwidth',
                doctype = 'tex')


class MyHtml(pweave.PwebFormatter):

    def preformat_chunk(self, chunk):
        if chunk['type'] == 'doc':
            return(chunk)
        
        chunk['content'] = highlight(chunk['content'], PythonLexer(), HtmlFormatter())
        #if len(chunk['results'].strip()) > 0:
        chunk['result'] = highlight(chunk['result'], PythonLexer(), HtmlFormatter()) 
        return(chunk)
    
    def initformat(self):
        self.formatdict = dict(codestart = '',
                               codeend = '',
                outputstart = '',
                outputend = '',
                figfmt = '.png',
                extension = 'html',
                width = '600',
                doctype = 'html')
        
    def formatfigure(self, chunk):
        figstring = ""
        for fig in chunk['figure']:
            figstring += ('<img src="%s" width="%s"/>' % (fig, chunk['width']))
        return(figstring)


class MDtoHTML(pweave.PwebHTMLFormatter):
    
    def __init__(self):
        pweave.PwebHTMLFormatter.__init__(self)
        #super(MDtoHTML, self).__init__()
        self.header = '<HTML><HEAD><link rel="stylesheet" href="pygments.css"/></HEAD><BODY>'
        self.footer = '</BODY></HTML>'

    before = []

    def preformat_chunk(self, chunk):
        MDtoHTML.before.append(chunk.copy())
        if chunk['type'] == "doc":
            chunk['content'] = markdown.markdown(chunk['content'])   
        return(chunk)
        
if sys.platform == 'cli':
	pass
#        pweave("sho.Rnw")
#        os.system("pdflatex sho.tex")
#        os.system("start sho.pdf")
else:
    #Tex
    doc = pweave.Pweb('ma-tex.Plw', "texminted")
    #doc = pweave.Pweb('sho.Rnw')
    #doc.setformat(Formatter = MyTex)
    #doc.documentationmode = False
    #pweave.Pweb.chunkformatters.append(formatcodechunk)
    #print(pweave.Pweb.chunkformatters[0].func_name)
    #doc.run()
    doc.weave()
    #doc.tangle()
    os.system('pdflatex -shell-escape ma-tex.tex')

    #Rst
    doc2 = pweave.Pweb('ma.Pnw')
    doc2.setformat('rst')
    doc2.documentationmode = False
    doc2.weave()
    os.system('rst2html ma.rst > ma-rst.html')

    #HTML
    doc3 = pweave.Pweb('ma2.htmlw')
    #pweave.Pweb.defaultoptions.update(wrap = False)
    #doc3.setformat(Formatter = MyHtml)
    doc3.setformat("html")
    doc3.weave()

    #Markdown to HTML
    doc4 = pweave.Pweb('ma.mdw')
    doc4.setformat(Formatter = MDtoHTML)
    doc4.weave()
    #print doc4.parsed[1]
    #print doc4.executed[1]
    #pprint(MDtoHTML.before)
    #print 
    

    
    
os.chdir('..')
