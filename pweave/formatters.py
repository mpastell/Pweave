

#Format chunks
#def formatdocchunk(chunk):
#    return(chunk['content'])

#A test formatter for custom call code
#def formatcapschunk(chunk):
#    return(chunk['content'].upper())

class PwebFormatter(object):

    def __init__(self):
        self.initformat()
        self._fillformatdict()

    def setexecuted(self, executed):
        self.executed = executed

    def format(self):
        self.formatted = []
        for chunk in self.executed:
            #Fill in default options, if they are not defined for a chunk
            for key in self.formatdict.keys():
                if not chunk.has_key(key):
                    chunk[key] = self.formatdict[key]
            
            #Wrap text if option is set
            if chunk['type'] is not "doc":
                if chunk['wrap']:
                    chunk['content'] = self._wrap(chunk['content'])
                    chunk['result'] = self._wrap(chunk['result'])

            
            #Preformat chunk content before default formatters
            chunk = self.preformat_chunk(chunk)

            if chunk['type'] is "doc":
                self.formatted.append(self.format_docchunk(chunk))
            elif chunk['type'] is "code":
                self.formatted.append(self.format_codechunks(chunk))
            else:
                self.formatted.append(chunk["content"])
        #print self.formatted

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
        if chunk['fig']:
            if chunk['include']:
                result += self.formatfigure(chunk)
            #Call figure formatting function
            #figstring = getattr(formatters, ('add%sfigure' % self.formatdict['doctype']))(chunk)
            #result += figstring
        return(result)
    
    def format_docchunk(self, chunk):
        return(chunk['content'])

    def getformatdict(self):
        return(self.formatdict)

    def getformatted(self):
        return(self.formatted)

    def updateformatdict(self, dict):
        self.formatdict.update(dict)

    def _wrapper(self, string, width = 75):
        """Wrap a string to specified width like Python terminal"""
        if len(string) < width:
            return string
        #Wrap also comment lines
        if string.lstrip()[0] is "#":
            return string[0:width] + '\n' + self._wrapper("#" + string[width:len(string)], width)
        else:
            return string[0:width] + '\n' + self._wrapper(string[width:len(string)], width)

    def _wrap(self, content):
        splitted = content.split("\n")
        result = ""
        for line in splitted:
            result += self._wrapper(line, 75) + '\n'
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

        for fig in fignames:
            figstring += ("\\includegraphics[width= %s]{%s}\n" % (width, fig)) 

        #Figure environment
        if chunk['caption']:
            result += ("\\begin{figure}\n"\
                        "%s"     
                        "\\caption{%s}\n" % (figstring, caption))
            if chunk.has_key("name"):
                result += "\label{%s}\n" % chunk['name']
            result += "\\end{figure}\n"

        else:
            result += figstring
        return(result)

class PwebRstFormatter(PwebFormatter):

    def initformat(self):
        self.formatdict = dict(codestart = '::\n',
                codeend = '\n\n',
                outputstart = '::\n',
                outputend = '\n\n',
                #rst has specific format (doctest) for term blocks
                termstart = '',
                termend = '\n\n',
                termindent = '',
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
        figname = chunk['figure']
        caption = chunk['caption']
        width = chunk['width']
        result = ""   
        
        if chunk['caption']:
            result += '![%s](%s)\n' % (caption, figname[0])
        else:
            result += '![](%s)\\\n' % (figname[0])
        return(result)

class PwebSphinxFormatter(PwebRstFormatter):

    def initformat(self):
          self.formatdict = dict(codestart = '::\n',
                codeend = '\n\n',
                outputstart = '.. code-block::\n',
                outputend = '\n\n',
                #rst has specific format (doctest) for term blocks
                termstart = '',
                termend = '\n\n',
                termindent = '',
                indent = '    ',
                #Sphinx determines the figure format automatically
                #for different output formats
                figfmt = '.*',
                savedformats = ['.png', '.pdf'],
                extension = 'rst',
                width = '15 cm',
                doctype = 'rst')

    def formatfigure(self, chunk):
        figname = chunk['figure']
        caption = chunk['caption']
        width = chunk['width']
        result = ""   

        if chunk['caption']:
            result += (".. figure:: %s\n"\
                        "   :width: %s\n\n"\
                        "   %s\n\n" % (figname[0], width, caption))
        else:
            result += ('.. image:: %s\n   :width: %s\n\n'   % (figname[0], width))
        return(result)

class PwebHTMLFormatter(PwebFormatter):

    def format_codechunks(self, chunk):
        from pygments import highlight
        from pygments.lexers import PythonLexer
        from pygments.formatters import HtmlFormatter, LatexFormatter
    
        chunk['content'] = highlight(chunk['content'], PythonLexer(), HtmlFormatter())
        if len(chunk['result'].strip()) > 0 and chunk['results'] is 'verbatim':
            chunk['result'] = highlight(chunk['result'], PythonLexer(), HtmlFormatter()) 
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
            result += ("<figure>\n"\
                        "%s"     
                        "<figcaption>%s</figcaption>\n</figure>" % (figstring, chunk['caption']))
             

        else:
            result += figstring
        return(result)
        
            
        return(figstring)

