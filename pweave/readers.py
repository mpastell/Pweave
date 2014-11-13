#Pweave readers
import re
import sys
import copy
import json
from subprocess import Popen, PIPE


class PwebReader(object):
    """Reads and parses Pweb documents"""
    # regex that matches beginning of code block
    code_begin = r"^\s*<<(.*)>>=$"
    doc_begin = r"^@$"

    def __init__(self, file = None, string = None):    
        self.source = file
        #Get input from string or 
        if file != None:
            codefile = open(self.source, 'r')
            self.rawtext = codefile.read()
            codefile.close()
        else:
            self.rawtext = string
        self.state = "doc" #Initial state of document


    def getparsed(self):
        return(copy.deepcopy(self.parsed))

    def count_emptylines(self, line):
        """Counts empty lines for parser, the result is stored in self.n_emptylines"""
        if line.strip() == "":
            self.n_emptylines += 1
        else:
            self.n_emptylines = 0

    def codestart(self, line):
        if not re.match(self.code_begin, line):
            return ((False, True))
        else:
            return ((True, True))

    def docstart(self, line):
        if not re.match(self.doc_begin, line.strip()):
            return ((False, True))
        else:
            return ((True, True))

    def parse(self):
        lines = self.rawtext.splitlines()

        read = ""
        chunks = []
        codeN = 1
        docN = 1
        opts = self.getoptions("")
        self.n_emptylines = 0
        self.lineNo = 0

        for line in lines:

            (code_starts, skip) = self.codestart(line)
            if code_starts:  #and self.state != "code":
                if self.state == "doc":
                    docN +=1
                    chunks.append({"type" : "doc", "content" : read, "number" : docN})
                else:
                    chunks.append( {"type" : "code", "content" : "\n" + read.rstrip(), 
                                    "number" : codeN, "options" : opts})
                    codeN +=1

                opts = self.getoptions(line)
                self.state = "code"                                
                read = ""
                if skip:
                    continue #Don't append options code

            (doc_starts, skip) = self.docstart(line)
            if doc_starts and self.state =="code":
                self.state = "doc"
                if read.strip() != "" or opts.has_key("source"): #Don't parse empty chunks unless source is specified
                    chunks.append( {"type" : "code", "content" : "\n" + read.rstrip(), 
                                    "number" : codeN, "options" : opts})
                codeN +=1
                read = ""
                if skip:
                    continue

            if self.state == "doc":
                if hasattr(self, "strip_comments"):
                    line = self.strip_comments(line)

            read += line + "\n"
            self.count_emptylines(line)
            self.lineNo += 1

        #Handle the last chunk
        if self.state == "code":
            chunks.append( {"type" : "code", "content" : "\n" + read.rstrip(), 
                                    "number" : codeN, "options" : opts})
        if self.state == "doc":
            chunks.append({"type" : "doc", "content" : read, "number" : docN})
        self.parsed = chunks


    def getoptions(self, opt):
        # Aliases for False and True to conform with Sweave syntax
        FALSE = False
        TRUE = True

        #Parse options from chunk to a dictionary
        optstring = opt.replace('<<', '').replace('>>=', '').strip()
        if not optstring:
            return({})
        #First option can be a name/label
        if optstring.split(',')[0].find('=')==-1:
            splitted = optstring.split(',')
            splitted[0] = 'name = "%s"' % splitted[0]
            optstring = ','.join(splitted)

        exec("chunkoptions =  dict(" + optstring + ")")
        if chunkoptions.has_key('label'):
            chunkoptions['name'] = chunkoptions['label']

        return(chunkoptions)

class PwebScriptReader(PwebReader):
    """Read scripts to Pweave"""
    
    def __init__(self, file = None, string = None):
        PwebReader.__init__(self, file, string)
        self.state = "code" #Initial state

    def count_emptylines(self, line):
        """Counts empty lines for parser, the result is stored in self.n_emptylines"""
        if line.strip() == "":
            self.n_emptylines += 1
        else:
            self.n_emptylines = 0

    def codestart(self, line):
      if line.startswith("#+"):
          starts = True
      elif self.state != "code" and (not line.startswith("#'") and self.n_emptylines > 0):
          starts = True
      else:
          starts = False
      skip =  line.startswith("#+")
      return((starts, skip))

    def docstart(self, line):
        return((line.startswith("#'"), False))

    def strip_comments(self, line):
        if line == "#'":
            line = line.replace("#'", "")
        else:
            line = line.replace("#' ", "", 1) 
        return(line)

    def getoptions(self, opt):
        if not opt.startswith("#+ "):
            return({})

        # Aliases for False and True to conform with Sweave syntax
        FALSE = False
        TRUE = True
        #Parse options from chunk to a dictionary
        optstring = opt.replace('#+', '', 1).strip()
        if not optstring:
            return({})
        #First option can be a name/label
        if optstring.split(',')[0].find('=')==-1:
            splitted = optstring.split(',')
            splitted[0] = 'name = "%s"' % splitted[0]
            optstring = ','.join(splitted)

        exec("chunkoptions =  dict(" + optstring + ")")
        #Update the defaults
        
        if chunkoptions.has_key('label'):
            chunkoptions['name'] = chunkoptions['label']

        return(chunkoptions)

class PwebNBReader(object):
    """Read IPython notebooks"""

    def __init__(self, file = None, string = None):
        self.source = file
        self.NB = json.loads(open(file).read())

    def parse(self):
        doc = self.NB['worksheets'][0]['cells']

        self.parsed = []
        docN = 1
        codeN = 1

        for cell in doc:
            if cell['cell_type'] == "code":
                self.parsed.append({'type' : "code", "content" : "\n" + "".join(cell['input']), "options" : {}, "number" : codeN})
                codeN += 1
            else:
                self.parsed.append({'type' : "doc", "content" : "\n" + "".join(cell['source']), "options" : {}, "number" : docN})
                docN +=1

    def getparsed(self):
        return(copy.deepcopy(self.parsed))

class PwebReaders(object):
    """Lists available input formats"""
    formats = {'noweb' : {'class' : PwebReader, 'description' :  'Noweb document'},
               'script' : {'class' : PwebScriptReader, 'description' :  'Script format'},
               'notebook' : {'class' : PwebNBReader, 'description' :  'IPython notebook'}
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
        print("\nPweave supported input formats:\n")
        print(cls.getformats())
        print("More info: http://mpastell.com/pweave/ \n")    

class PwebConvert(object):
    """Convert from one input format to another"""

    def __init__(self, file = None, informat = "script", outformat = "noweb", pandoc_args= None):
        self.informat = informat
        self.outformat = outformat
        
        self.doc = PwebReaders.formats[informat]['class'](file)
        
        self.pandoc_args = pandoc_args
        if self.informat == self.outformat:
            self.basename =  re.split("\.+[^\.]+$", file)[0] + "_converted"
        else:
            self.basename =  re.split("\.+[^\.]+$", file)[0]
        self.doc.parse()
        self.convert()
        self.write()


    def format_docchunk(self, content):
        """Format doc chunks for output"""
        if self.pandoc_args is not None:
            pandoc = Popen(["pandoc"] + self.pandoc_args.split(), stdin = PIPE, stdout = PIPE)
            pandoc.stdin.write(content)
            content = (pandoc.communicate()[0]).replace("\r", "") + "\n"

        if self.outformat == "noweb":
            return(content)
        if self.outformat == "script":
            lines = content.splitlines()
            flines = [("#' " + x) for x in lines]
            return("\n".join(flines))

    def write(self):
        if self.outformat == "noweb":
            ext = ".Pnw"
        if self.outformat == "script":
            ext = ".py"
        file = self.basename + ext
        f = open(file, "w")
        f.write(self.converted)
        f.close()
        print "Output written to " + file
        
    def convert(self):
        output = []

        if self.outformat == "noweb":
           code = "<<%s>>=%s\n@\n"
        if self.outformat == "script":
           code = "#+ %s\n%s\n"

        for chunk in self.doc.parsed:
                if chunk["type"] == "doc":
                    output.append(self.format_docchunk(chunk["content"]))
                if chunk["type"] == "code":
                    optstring = self.get_optstring(chunk)
                    output.append(code % (optstring, chunk["content"]))

        self.converted = "\n".join(output)

    def get_optstring(self, chunk):
        optstring = ""
        n = len(chunk["options"].keys())
        i = 0
        for key in chunk["options"].keys():
            i +=1
            if type(chunk["options"][key]) == bool:
                optstring += key + '=' + str(chunk["options"][key])
            else:
                optstring += key + '="' + str(chunk["options"][key]) + '"'
            if (i < n):
                optstring += ", "

        return(optstring)

#pweb is imported here to avoid import loop
import pweb

