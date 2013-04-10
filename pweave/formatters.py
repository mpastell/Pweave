

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
        self.formatted = map(self._formatchunks, self.executed)

    def getformatdict(self):
        return(self.formatdict)

    def getformatted(self):
        return(self.formatted)

    def _formatchunks(self, chunk):

        #add formatdict to the same with chunks dictionary, makes formatting
        #commands more compact and makes options available for custom
        #formatters

        #Fill in default options, if they are not defined for a chunk
        for key in self.formatdict:
            if not chunk.has_key(key):
                chunk["key"] = self.formatdict[key]

        #chunk.update(self.formatdict) #Old way with a bug

        ## Call custom formatters
        #chunk = self._getformatter(chunk)

        #if chunk is not None and type(chunk)!=dict:
        #    return(chunk)
        #if chunk is None:
        #    return('UNKNOWN CHUNK TYPE: %s \n' % chunk['type'])

        #A doc chunk
        if chunk['type'] == 'doc':
             return(chunk['content'])

        chunk['content'] = self._indent(chunk['content'])


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
            if chunk['echo'] and chunk['results'] != 'hidden':
                chunk['result'] = self._termindent(chunk['result'])
                result = '%(termstart)s%(result)s%(termend)s' % chunk


        #Other things than term
        elif chunk['evaluate'] and chunk ['echo'] and chunk['results'] == 'verbatim':
            result = '%(codestart)s%(content)s%(codeend)s' % chunk
            if len(chunk['result']) > 1:
                    chunk['result'] = self._indent(chunk['result'])
                    result += '%(outputstart)s%(result)s%(outputend)s' % chunk

        elif chunk['evaluate'] and chunk ['echo'] and chunk['results'] != 'verbatim':
                chunk['result'] = chunk['result'].replace('\n', '', 1)
                result = '%(codestart)s%(content)s%(codeend)s%(result)s' % chunk

        elif chunk['evaluate'] and not chunk['echo'] and chunk['results'] == 'verbatim':
            if len(chunk['result']) > 1:
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
            result += self.formatfigure(chunk)
            #Call figure formatting function
            figstring = getattr(formatters, ('add%sfigure' % self.formatdict['doctype']))(chunk)

            result += figstring
        return(result)
    
    def _fillformatdict(self):
        """Fill in the blank options that are now only used for rst
            but also allow e.g. special latex style for terminal blocks etc."""
        self._fillkey('termstart', self.formatdict['codestart'])
        self._fillkey('termindent', self.formatdict['indent'])
        self._fillkey('termend', self.formatdict['codeend'])
        self._fillkey('savedformats', list([self.formatdict['figfmt']]))

    def _fillkey(self, key, value):
        if not self.formatdict.has_key(key):
            self.formatdict[key] = value

class PwebTexFormatter(PwebFormatter):

    def __init__(self):
        PwebFormatter.__init__(self)
                
    def initformat(self):
        self.formatdict = dict(codestart = '\\begin{verbatim}',
                codeend = '\end{verbatim}\n',
                outputstart = '\\begin{verbatim}',
                outputend = '\end{verbatim}\n',
                indent = '',
                figfmt = '.pdf',
                extension = 'tex',
                width = '\\textwidth',
                doctype = 'tex')

    def formatfigure(self, chunk):
        figname = chunk['figure']
        caption = chunk['caption']
        width = chunk['width']
        label = chunk['label']
        result = ""   

        if chunk['caption']:
            result += ("\\begin{figure}\n"\
                        "\\includegraphics[width= %s]{%s}\n"\
                        "\\caption{%s}\n"\
                        "\\label{%s}\n"\
                        "\end{figure}\n" % (width, figname, label, caption))
        else:
            result += "\\includegraphics[width=%s]{%s}\n" % (width, figname)
        return(result)






#Format figures

  


def addrstfigure(chunk):
    figname = chunk['figure']
    caption = chunk['caption']
    width = chunk['width']
    result = ""   

    if chunk['caption']:
        result += (".. figure:: %s\n"\
                    "   :width: %s\n\n"\
                    "   %s\n\n" % (figname, width, caption))
    else:
        result += ('.. image:: %s\n   :width: %s\n\n'   % (figname, width))
    return(result)
     
def addpandocfigure(chunk):
    figname = chunk['figure']
    caption = chunk['caption']
    width = chunk['width']
    result = ""   
        
    if chunk['caption']:
        result += '![%s](%s)\n' % (caption, figname)
    else:
        result += '![](%s)\\\n' % (figname)
    return(result)

def addsphinxfigure(chunk):
    figname = chunk['figure']
    caption = chunk['caption']
    width = chunk['width']
    result = ""   

    if chunk['caption']:
        result += (".. figure:: %s\n"\
                    "   :width: %s\n\n"\
                    "   %s\n\n" % (figname, width, caption))
    else:
        result += ('.. image:: %s\n   :width: %s\n\n'   % (figname, width))
    return(result)

def wrapper(string, width):
    """Wrap a string to specified width like Python terminal"""
    if len(string) < width:
        return string
    return string[0:width] + '\n' + wrapper(string[width:len(string)], width)