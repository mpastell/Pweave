#Pweave readers
import re
import sys
import copy


class PwebReader(object):
    """Reads and parses Pweb documents"""

    def __init__(self, file = None, string = None):
        
        self.source = file

        #Get input from string or 
        if file != None:
            codefile = open(self.source, 'r')
            self.rawtext = codefile.read()
            codefile.close()
        else:
            self.rawtext = string

    def parse(self):
        #Prepend "@\n" to code in order to
        #ChunksToDict to work with the first text chunk
        code = "@\n" + self.rawtext
        #Split file to list at chunk separators
        chunksep = re.compile('(^<<.*?>>=[\s]*$)|(@[\s]*?$)', re.M)
        codelist = chunksep.split(code)
        codelist = filter(lambda x : x != None, codelist)
        codelist = filter(lambda x :  not x.isspace() and x != "", codelist)
        #Make a tuple for parsing
        codetuple = self._chunkstotuple(codelist)
        #Parse code+options and text chunks from the tuple
        parsedlist = map(self._chunkstodict, codetuple)
        parsedlist = filter(lambda x: x != None, parsedlist)
        #number codechunks, start from 1
        n = 1
        for chunk in parsedlist:
            if chunk['type'] == 'code':
                chunk['number'] = n
                n += 1
        #Remove extra line inserted during parsing
        parsedlist[0]['content'] =  parsedlist[0]['content'].replace('\n', '', 1)

        self.parsed = parsedlist
        self.isparsed = True

    def getparsed(self):
        return(copy.deepcopy(self.parsed))

    def _chunkstodict(self, chunk):
        if (re.findall('@[\s]*?$', chunk[0])) and not (re.findall('^<<.*?>>=[\s]*$', chunk[1], re.M)):
            return({'type' : 'doc', 'content':chunk[1]})
        if (re.findall('^<<.*>>=[\s]*?$', chunk[0], re.M)):
            codedict = {'type' : 'code', 'content':chunk[1]}
            codedict.update(self._getoptions(chunk[0]))
            return(codedict)

    def _chunkstotuple(self, code):
        # Make a list of tuples from the list of chuncks
        a = list()

        for i in range(len(code)-1):
            x = (code[i], code[i+1])
            a.append(x)
        return(a)

    def _getoptions(self, opt):
        defaults = pweb.Pweb.defaultoptions.copy()

        # Aliases for False and True to conform with Sweave syntax
        FALSE = False
        TRUE = True


        #Parse options from chunk to a dictionary
        optstring = opt.replace('<<', '').replace('>>=', '').strip()
        if not optstring:
            return(defaults)
        #First option can be a name/label
        if optstring.split(',')[0].find('=')==-1:
            splitted = optstring.split(',')
            splitted[0] = 'name = "%s"' % splitted[0]
            optstring = ','.join(splitted)

        exec("chunkoptions =  dict(" + optstring + ")")
        #Update the defaults
        defaults.update(chunkoptions)
        if defaults.has_key('label'):
            defaults['name'] = defaults['label']

        return(defaults)

class PwebSpinReader(PwebReader):
    
    def __init__(self, file = None, string = None):
        PwebReader.__init__(self, file, string)

    def count_emptylines(self, line):
        """Counts empty lines for parser, the result is stored in self.n_emptylines"""
        if line.strip() == "":
            self.n_emptylines += 1
        else:
            self.n_emptylines = 0

    def codestart(self, line):
      starts = line.startswith("#+") or (not line.startswith("#' ") and self.n_emptylines > 0)
      skip =  line.startswith("#+")
      return((starts, skip))

    def docstart(self, line):
        return(line.startswith("#' "))

    def strip_comments(self, line):
        line = line.replace("#' ", "", 1) 
        return(line)

    def parse(self):
        lines = self.rawtext.splitlines()

        self.state = "code"
        read = ""
        chunks = []
        codeN = 1
        docN = 1
        opts = self.getoptions("")
        self.n_emptylines = 0
        self.lineNo = 0

        for line in lines:

            (code_starts, skip) = self.codestart(line)
            if code_starts  and self.state != "code":
                self.state = "code"
                if line.startswith("#+"):
                    opts = self.getoptions(line)
                else: 
                    opts = self.getoptions("")
                chunks.append({"type" : "doc", "content" : read, "number" : docN})
                docN +=1
                read = ""
                if skip:
                    continue #Don't append options code
            if self.docstart(line) and self.state =="code":
                self.state = "doc"
                if read.strip() != "":
                    chunk = {"type" : "code", "content" : "\n" + read.rstrip(), "number" : codeN}
                    codeN +=1
                    chunk.update(opts)
                    chunks.append(chunk.copy())
                read = ""

            if self.state == "doc":
                line = self.strip_comments(line)

            read += line + "\n"
            self.count_emptylines(line)
            self.lineNo += 1

        #Handle the last chunk
        if self.state == "code":
            chunk = {"type" : "code", "content" : "\n" + read.rstrip(), "number" : codeN}
            chunk.update(opts)
            chunks.append(chunk.copy())
        if self.state == "doc":
            chunks.append({"type" : "doc", "content" : read, "number" : docN})
        self.parsed = chunks

    def getoptions(self, opt):
        defaults = pweb.Pweb.defaultoptions.copy()

        # Aliases for False and True to conform with Sweave syntax
        FALSE = False
        TRUE = True
        #Parse options from chunk to a dictionary
        optstring = opt.replace('#+', '', 1).strip()
        if not optstring:
            return(defaults)
        #First option can be a name/label
        if optstring.split(',')[0].find('=')==-1:
            splitted = optstring.split(',')
            splitted[0] = 'name = "%s"' % splitted[0]
            optstring = ','.join(splitted)

        exec("chunkoptions =  dict(" + optstring + ")")
        #Update the defaults
        defaults.update(chunkoptions)
        if defaults.has_key('label'):
            defaults['name'] = defaults['label']

        return(defaults)
    



#pweb is imported here to avoid import loop
import pweb

