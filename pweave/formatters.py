import sys
from subprocess import Popen, PIPE
import textwrap
# Pweave output formatters


class PwebFormatter(object):

    def __init__(self, source = None):
        self.initformat()
        self._fillformatdict()
        self.header = None
        self.footer = None
        self.source = source
        self.wrapper = textwrap.TextWrapper(subsequent_indent = "", break_long_words = False)

    def setexecuted(self, executed):
        self.executed = executed

    def format(self):
        self.formatted = []
        for chunk in self.executed:
            #Fill in options for code chunks
            if chunk['type'] == "code":
                for key in self.formatdict.keys():
                    if not chunk.has_key(key):
                        chunk[key] = self.formatdict[key]
            
            #Wrap text if option is set
            if chunk['type'] == "code":
                if chunk['wrap'] == True:
                    chunk['content'] = self._wrap(chunk['content'])
                    chunk['result'] = self._wrap(chunk['result'])
                if chunk['wrap'] == 'code':
                    chunk['content'] = self._wrap(chunk['content'])
                if chunk['wrap'] == 'results':
                    chunk['result'] = self._wrap(chunk['result'])
            
            #Preformat chunk content before default formatters
            chunk = self.preformat_chunk(chunk)

            if chunk['type'] == "doc":
                self.formatted.append(self.format_docchunk(chunk))
            elif chunk['type'] == "code":
                self.formatted.append(self.format_codechunks(chunk))
            else:
                self.formatted.append(chunk["content"])

        
        #Flatten to string, make conversion and headers etc.

        for i in range(len(self.formatted)):
            self.formatted[i] = self.formatted[i].decode('utf-8')
        self.formatted = "\n".join(self.formatted)
        self.convert() #Convert to e.g. markdown
        self.add_header()
        self.add_footer()
        #print self.formatted

    def convert(self):
        pass
        

    def preformat_chunk(self, chunk):
        """You can use this method in subclasses to preformat chunk content""" 
        return(chunk)

    def format_termchunk(self, chunk):    
        if chunk['echo'] and chunk['results'] != 'hidden':
            chunk['result'] = self._termindent(chunk['result'])
            result = '%(termstart)s%(result)s%(termend)s' % chunk
        else:
            result = ""
        return(result)

    def format_codeblock(self, chunk):
        pass

    def format_results(self, chunk):
        pass

    def format_codechunks(self, chunk):

        chunk['content'] = self._indent(chunk['content'])

        #Ugly fix to extra whitespace after chunks, 
        #should really find out where extra whitespace comes from
        #chunk['result'] = chunk['result'].rstrip() + "\n"
        
        #Implement this for clarity
        #content = self.format_codeblock(chunk)
        #results = format_results(chunk)
        #return(content + results)

        #Code is not executed
        if not chunk['evaluate']:
            if chunk['echo']:
                result = '%(codestart)s%(content)s%(codeend)s' % chunk
                return(result)
            else:
                return('')

        #Code is executed
        #-------------------        
        result = ""

        #Hidden results
        if chunk['results'] == 'hidden':
            chunk['result'] = ''

        #Term sets echo to true
        if chunk['term']:
           result = self.format_termchunk(chunk)
        #Other things than term
        elif chunk['evaluate'] and chunk ['echo'] and chunk['results'] == 'verbatim':
            result = '%(codestart)s%(content)s%(codeend)s' % chunk
            if len(chunk['result'].strip()) > 1:
                    chunk['result'] = self._indent(chunk['result'])
                    result += '%(outputstart)s%(result)s%(outputend)s' % chunk

        elif chunk['evaluate'] and chunk ['echo'] and chunk['results'] != 'verbatim':
                chunk['result'] = chunk['result'].replace('\n', '', 1)
                result = '%(codestart)s%(content)s%(codeend)s%(result)s' % chunk

        elif chunk['evaluate'] and not chunk['echo'] and chunk['results'] == 'verbatim':
            if len(chunk['result'].strip()) > 1:
                chunk['result'] = self._indent(chunk['result'])
                result += '%(outputstart)s%(result)s%(outputend)s' % chunk

        elif chunk['evaluate'] and not chunk['echo']:
                #Remove extra line added when results are captured in run phase
                result = chunk['result'].replace('\n', '', 1)
        #else:
            #This a test to see if all options have been captured
            #result = "\\large{NOT YET IMPLEMENTED!!\n}"
            #result += str(chunk)


        #Handle figures
        if chunk['fig'] and chunk.has_key("figure"):
            if chunk['include']:
                result += self.formatfigure(chunk)
            #Call figure formatting function
            #figstring = getattr(formatters, ('add%sfigure' % self.formatdict['doctype']))(chunk)
            #result += figstring
        return(result)
    
    def format_docchunk(self, chunk):
        return(chunk['content'])

    def add_header(self):
        """Can be used to add header to self.formatted list"""
        if self.header is not None:
            self.formatted = self.header + self.formatted

    def add_footer(self):
        """Can be used to add footer to self.formatted list"""
        if self.footer is not None:
            self.formatted += self.footer

    def getformatdict(self):
        return(self.formatdict)

    def getformatted(self):
        return(self.formatted.encode('utf-8'))

    def updateformatdict(self, dict):
        self.formatdict.update(dict)

    def _wrapper(self, string, width = 80):
        """Wrap a string to specified width like Python terminal"""
        if len(string) < width:
            return string
        #Wrap also comment lines
        if string.lstrip()[0] == "#":
            return string[0:width] + '\n' + self._wrapper("#" + string[width:len(string)], width)
        else:
            return string[0:width] + '\n' + self._wrapper(string[width:len(string)], width)

    def _wrap(self, content):
        splitted = content.split("\n")
        result = ""
        for line in splitted:
            result += self.wrapper.fill(line) + '\n'
        return(result)

    def _fillformatdict(self):
        """Fill in the blank options that are now only used for rst
            but also allow e.g. special latex style for terminal blocks etc."""
        self._fillkey('termstart', self.formatdict['codestart'])
        self._fillkey('termend', self.formatdict['codeend'])
        self._fillkey('savedformats', list([self.formatdict['figfmt']]))

    def _fillkey(self, key, value):
        if not self.formatdict.has_key(key):
            self.formatdict[key] = value

    def _indent(self, text):
        """Indent blocks for formats where indent is significant"""
        return(text)
        #return(text.replace('\n', '\n' + self.formatdict['indent']))

    def _termindent(self, text):
        """Indent blocks for formats where indent is significant"""
        return(text)
        #return(text.replace('\n', '\n' + self.formatdict['termindent']))

class PwebTexFormatter(PwebFormatter):
                
    def initformat(self):
        self.formatdict = dict(codestart = '\\begin{verbatim}',
                codeend = '\end{verbatim}\n',
                outputstart = '\\begin{verbatim}',
                outputend = '\end{verbatim}\n',
                figfmt = '.pdf',
                extension = 'tex',
                width = '\\textwidth',
                doctype = 'tex')

    def formatfigure(self, chunk):

        fignames = chunk['figure']
        caption = chunk['caption']
        width = chunk['width']
        result = ""        
        figstring = ""

        if chunk["f_env"] != None:
            result += "\\begin{%s}\n" % chunk["f_env"]

        for fig in fignames:
            figstring += ("\\includegraphics[width= %s]{%s}\n" % (width, fig)) 

        #Figure environment
        if chunk['caption']:
            result += ("\\begin{figure}[%s]\n"\
                        "\\center\n"\
                        "%s"     
                        "\\caption{%s}\n" % (chunk['f_pos'] ,figstring, caption))
            if chunk.has_key("name"):
                result += "\label{fig:%s}\n" % chunk['name']
            result += "\\end{figure}\n"

        else:
            result += figstring

        if chunk["f_env"] != None:
            result += "\\end{%s}\n" % chunk["f_env"]

        return(result)

class PwebMintedFormatter(PwebTexFormatter):
                
    def initformat(self):
        
        self.formatdict = dict(
             codestart = r'\begin{minted}[mathescape, fontsize=\small, xleftmargin=0.5em]{python}',
             codeend = '\end{minted}\n',
             outputstart = r'\begin{minted}[fontsize=\small, xleftmargin=0.5em, mathescape, frame = leftline]{text}',
             outputend = '\end{minted}\n',
             termstart = r'\begin{minted}[fontsize=\footnotesize, xleftmargin=0.5em, mathescape]{python}',
             termend = '\end{minted}\n',
             figfmt = '.pdf',
             extension = 'tex',
             width = '\\textwidth',
             doctype = 'tex')

class PwebTexPygmentsFormatter(PwebTexFormatter):

     def initformat(self):
        
        self.formatdict = dict(
             codestart = "",
             codeend = "",
             outputstart = "",
             outputend = "",
             termstart = "",
             termend = "",
             figfmt = '.pdf',
             extension = 'tex',
             width = '\\textwidth',
             doctype = 'tex')

     def format_codechunks(self, chunk):
        from pygments import highlight
        from pygments.lexers import PythonLexer, TextLexer, PythonConsoleLexer
        #from IPythonLexer import IPythonLexer
        from pygments.formatters import LatexFormatter
    
        chunk['content'] = highlight(chunk['content'], PythonLexer(), LatexFormatter(verboptions="frame=single,fontsize=\small, xleftmargin=0.5em"))
        if len(chunk['result'].strip()) > 0 and chunk['results'] == 'verbatim':
            if chunk['term']:
                chunk['result'] = highlight(chunk['result'], PythonLexer(), LatexFormatter(verboptions="frame=single,fontsize=\small, xleftmargin=0.5em")) 
            else:
                chunk['result'] = highlight(chunk['result'], TextLexer(), LatexFormatter(verboptions="frame=leftline,fontsize=\small, xleftmargin=0.5em")) 
        return(PwebFormatter.format_codechunks(self, chunk))

class PwebTexPweaveFormatter(PwebTexFormatter):
    """User defined formatting for chunks in header using pweavecode, pweaveoutput and pweaveterm environments"""
    def initformat(self):
        
        self.formatdict = dict(
             codestart = r'\begin{pweavecode}',
             codeend = '\end{pweavecode}\n',
             outputstart = r'\begin{pweaveout}',
             outputend = '\end{pweaveout}\n',
             termstart = r'\begin{pweaveterm}',
             termend = '\end{pweaveterm}\n',
             figfmt = '.pdf',
             extension = 'tex',
             width = '\\textwidth',
             doctype = 'tex')

class PwebRstFormatter(PwebFormatter):

    def initformat(self):
        self.formatdict = dict(codestart = '.. code:: python\n',
                codeend = '\n\n',
                outputstart = '.. code::\n',
                outputend = '\n\n',
                #rst has specific format (doctest) for term blocks
                termstart = '.. code:: python\n',
                termend = '\n\n',
                termindent = '    ',
                indent = '    ',
                figfmt = '.png',
                extension = 'rst',
                width = '15 cm',
                doctype = 'rst')

    def formatfigure(self, chunk):
        fignames = chunk['figure']
        caption = chunk['caption']
        width = chunk['width']
        result = ""
        figstring = ""

        for fig in fignames:
            figstring += ('.. image:: %s\n   :width: %s\n\n'   % (fig, width))    

        if chunk['caption']:
            result += (".. figure:: %s\n"\
                        "   :width: %s\n\n"\
                        "   %s\n\n" % (fignames[0], width, caption))
        else:
            result += figstring
        return(result)

    def _indent(self, text):
        """Indent blocks for formats where indent is significant"""
        return(text.replace('\n', '\n' + self.formatdict['indent']))

    def _termindent(self, text):
        return(text.replace('\n', '\n' + self.formatdict['termindent']))

class PwebPandocFormatter(PwebFormatter):

    def initformat(self):
            self.formatdict = dict(codestart = '~~~~{.python}',
                codeend = '~~~~~~~~~~~~~\n\n',
                outputstart = '~~~~{.python}',
                outputend = '~~~~~~~~~~~~~\n\n',
                indent = '',
                termindent = '',
                figfmt = '.png',
                extension = 'md',
                width = '15 cm',
                doctype = 'pandoc')
     
    def formatfigure(self, chunk):
        fignames = chunk['figure']
        caption = chunk['caption']
        width = chunk['width']
        result = ""
        figstring = ""

        for fig in fignames:
            figstring += '![](%s)\\\n' % (fig)
            
        if chunk['caption']:
            result += '![%s](%s)\n' % (caption, fignames[0])
        else:
            result += figstring 
        return(result)

class PwebSphinxFormatter(PwebRstFormatter):

    def initformat(self):
          self.formatdict = dict(codestart = '.. code-block:: python\n',
                codeend = '\n\n',
                outputstart = '::\n',
                outputend = '\n\n',
                #rst has specific format (doctest) for term blocks
                termstart = '.. code-block:: python\n',
                termend = '\n\n',
                termindent = '    ',
                indent = '    ',
                #Sphinx determines the figure format automatically
                #for different output formats
                figfmt = '.*',
                savedformats = ['.png', '.pdf'],
                extension = 'rst',
                width = '15 cm',
                doctype = 'rst')

    def formatfigure(self, chunk):
        fignames = chunk['figure']
        caption = chunk['caption']
        width = chunk['width']
        result = ""
        figstring = ""

        for fig in fignames:
            figstring += ('.. image:: %s\n   :width: %s\n\n'   % (fig, width))    

        if chunk['caption']:
            result += (".. figure:: %s\n"\
                        "   :width: %s\n\n"\
                        "   %s\n\n" % (fignames[0], width, caption))
        else:
            result += figstring
        return(result)   
       
class PwebHTMLFormatter(PwebFormatter):

    def format_codechunks(self, chunk):
        from pygments import highlight
        from pygments.lexers import PythonLexer, PythonConsoleLexer, TextLexer
        from pygments.formatters import HtmlFormatter
    
        chunk['content'] = highlight(chunk['content'], PythonLexer(), HtmlFormatter())
        if len(chunk['result'].strip()) > 0 and chunk['results'] == 'verbatim':
            if chunk['term']:
                chunk['result'] = highlight(chunk['result'], PythonLexer(), HtmlFormatter()) 
            else:
                chunk['result'] = highlight(chunk['result'], TextLexer(), HtmlFormatter()) 

        return(PwebFormatter.format_codechunks(self, chunk))
    
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
        result = ""
        figstring = ""
        for fig in chunk['figure']:
            figstring += ('<img src="%s" width="%s"/>\n' % (fig, chunk['width']))

        #Figure environment
        if chunk['caption']:
            #Write labels as data-attribute for javascript etc.
            if chunk['name']:
                labelstring = 'data-label = "fig:%s"' % chunk["name"]
            else:
                labelstring = ""

            result += ("<figure>\n"\
                        "%s"     
                        "<figcaption %s>%s</figcaption>\n</figure>" % (figstring, labelstring, chunk['caption']))
             

        else:
            result += figstring
        return(result)
        
            
        return(figstring)

class PwebMDtoHTMLFormatter(PwebHTMLFormatter):

    def __init__(self, source):
        from templates import htmltemplate
        from . import __version__
        import time
        PwebHTMLFormatter.__init__(self, source)
        self.header = htmltemplate["header"]
        self.footer = (htmltemplate["footer"] % 
                      {"source" : self.source, "version" : __version__, "time" : time.strftime("%d-%m-%Y", time.localtime())}) 

    
       

    def parsetitle(self, chunk):
        """Parse titleblock from first doc chunk, like Pandoc"""
        lines = chunk['content'].splitlines()
        if len(lines) > 3:
            if lines[0].startswith("%"):
                lines[0] = '<H1 class = "title">%s</H1>' %  (lines[0].replace("%", "", ))
                if lines[1].startswith("%"):
                    lines[1] = '<strong>Author:</strong> %s <BR/>' %  (lines[1].replace("%", "", ))
                if lines[2].startswith("%"):
                    lines[2] = '<strong>Date:</strong> %s <BR/>' %  (lines[2].replace("%", "", ))
        chunk['content'] = ("\n").join(lines)
        return(chunk)


    def format_docchunk(self, chunk):
        if chunk.has_key("number") and chunk['number'] == 1:
            chunk = self.parsetitle(chunk)

        try:
            from markdown import markdown
        except:
            try:
                from markdown2 import markdown
            except:
                raise
        
        #Use Mathjax if it is available
        try:
            import markdown2Mathjax as MJ
            tmp = MJ.sanitizeInput(chunk['content'])
            markedDownText = markdown(tmp[0])
            finalOutput = MJ.reconstructMath(markedDownText,tmp[1], inline_delims=["\\(","\\)"])
            chunk['content'] = finalOutput
        except:
            sys.stderr.write("WARNING: Can't import markdown2Mathjax, expect problems with math formatting.\n")
            chunk['content'] = markdown(chunk['content'])
        return(chunk['content'])

class PwebPandocMDtoHTMLFormatter(PwebMDtoHTMLFormatter):
    
    def convert(self):
        try:
            pandoc = Popen(["pandoc", "--mathjax", "-t", "html", "-f", "markdown"], stdin = PIPE, stdout = PIPE)
        #pandoc = Popen(["pandoc.exe", "--mathjax"], stdin = PIPE, stdout = PIPE)
        except:
            sys.stderr.write("ERROR: Can't find pandoc")
            raise
        pandoc.stdin.write(self.formatted)
        self.formatted = pandoc.communicate()[0]
        #return(chunk['content'])
        

class PwebPandoctoTexFormatter(PwebTexPygmentsFormatter):

    def __init__(self, source = None):
        PwebTexPygmentsFormatter.__init__(self, source)
        from pygments.formatters import LatexFormatter
        x = LatexFormatter()
        self.header = (r"""\documentclass[a4paper,11pt,final]{article}
        \usepackage{fancyvrb, color, graphicx, hyperref, ,amsmath, url}
        \usepackage{palatino}
        \usepackage[a4paper,text={16.5cm,25.2cm},centering]{geometry}
        
        \hypersetup  
        {   pdfauthor = {Pweave},
            pdftitle={Published from %s},
            colorlinks=TRUE,
            linkcolor=black,
            citecolor=blue,
            urlcolor=blue
        }
        \setlength{\parindent}{0pt}
        \setlength{\parskip}{1.2ex}
        %s
        """) % (self.source, x.get_style_defs())
        self.footer = r"\end{document}"

    
    def parsetitle(self, chunk):
        """Parse titleblock from first doc chunk, like Pandoc"""
        lines = chunk['content'].splitlines()
        if len(lines) > 3:
            if lines[0].startswith("%"):
                self.header += '\n\\title{%s}\n' %  (lines[0].replace("%", "", ))
                lines[0] = ""
                if lines[1].startswith("%"):
                    self.header += '\\author{%s}\n' %  (lines[1].replace("%", "", ))
                    lines[1] = ""
                if lines[2].startswith("%"):
                    self.header += '\\date{%s}\n' %  (lines[2].replace("%", "", ))
                    lines[2] = ""
                self.header += "\n\\begin{document}\n\maketitle\n"
            #If there is no titleblock
            else:
                self.header += "\\begin{document}\n"

        chunk['content'] = ("\n").join(lines)
        return(chunk)


    def format_docchunk(self, chunk):
        if chunk.has_key("number") and chunk['number'] == 1:
            chunk = self.parsetitle(chunk)
        try:
            pandoc = Popen(["pandoc", "-t", "latex", "-f", "markdown"], stdin = PIPE, stdout = PIPE)
        except:
            sys.stderr.write("ERROR: Can't find pandoc")
            raise
        pandoc.stdin.write(chunk['content'])
        chunk['content'] = pandoc.communicate()[0]
        return(chunk['content'])
    
        #pandoc.stdin.write(self.formatted)
        #self.formatted = pandoc.communicate()[0]
        #self.formatted

class PwebFormats(object):
    """Contains a dictionary of available output formats"""
    formats = {'tex' : {'class' : PwebTexFormatter, 'description' :  'Latex with verbatim for code and results'},
               'texminted' : {'class' : PwebMintedFormatter, 'description' :  'Latex with predefined minted environment for codeblocks'},
               'texpweave' : {'class' : PwebTexPweaveFormatter, 'description' :  'Latex output with user defined formatting using named environments (in latex header)'},
               'texpygments' : {'class' : PwebTexPygmentsFormatter, 'description' :  'Latex output with pygments highlighted output'},
               'rst' : {'class' : PwebRstFormatter, 'description' :  'reStructuredText'}, 
               'pandoc' :  {'class' : PwebPandocFormatter, 'description' :  'Pandoc markdown'}, 
               'sphinx' : {'class' : PwebSphinxFormatter, 'description' :  'reStructuredText for Sphinx'}, 
               'html' : {'class' : PwebHTMLFormatter, 'description' :  'HTML with pygments highlighting'},
               'md2html' : {'class' : PwebMDtoHTMLFormatter, 'description' :  'Markdown to HTML using Python-Markdown'},
               'pandoc2latex' : {'class' : PwebPandoctoTexFormatter, 'description' :  'Markdown to Latex using Pandoc, requires Pandoc in path'},
               'pandoc2html' : {'class' : PwebPandocMDtoHTMLFormatter, 'description' :  'Markdown to HTML using Pandoc, requires Pandoc in path'}
               }
    
    @classmethod
    def shortformats(cls):
        fmtstring = ""
        names = cls.formats.keys()
        n = len(names)
        for i in range(n):
            fmtstring += (" %s") % (names[i])
            if i < (n-1):
                fmtstring += ","

        return(fmtstring)

    @classmethod
    def getformats(cls):
        fmtstring = "" 
        for format in sorted(cls.formats):
            fmtstring += ("* %s:\n   %s\n") % (format, cls.formats[format]['description'])
        return(fmtstring)

    @classmethod
    def listformats(cls):
        print("\nPweave supported output formats:\n")
        print(cls.getformats())
        print("More info: http://mpastell.com/pweave/formats.html \n")
        

    
    

