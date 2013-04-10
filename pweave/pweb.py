import os
import sys
import re
from cStringIO import StringIO
import code
import inspect
from . import formatters
from formatters import *
import cPickle as pickle



def pweave(file, doctype = 'rst', plot = True, useminted = False,
           docmode = False, cache = False,
           figdir = 'figures', cachedir = 'cache',
           figformat = None, returnglobals = True):
    """
    Processes a Pweave document and writes output to a file

    :param file: ``string`` input file
    :param doctype: ``string`` document format: 'sphinx', 'rst', 'pandoc' or 'tex'
    :param plot: ``bool`` use matplotlib (or Sho with Ironpython) 
    :param useminted: ``bool`` use minted package for code chunks in LaTeX documents
    :param docmode: ``bool`` use documentation mode, chunk code and results will be loaded from cache and inline code will be hidden
    :param cache: ``bool`` Cache results to disk for documentation mode
    :param figdir: ``string`` directory path for figures
    :param cachedir: ``string`` directory path for cached results used in documentation mode
    :param figformat: ``string`` format for saved figures (e.g. '.png'), if None then the default for each format is used
    :param returnglobals: ``bool`` if True the namespace of the executed document is added to callers global dictionary. Then it is possible to work interactively with the data while writing the document. IronPython needs to be started with -X:Frames or this won't work.
    """

    doc = Pweb(file)
    doc.setformat(doctype)
    if sys.platform == 'cli':
        Pweb.usesho = plot
        Pweb.usematplotlib = False
    else:
        Pweb.usematplotlib = plot
    if useminted:
        doc.useminted()
    Pweb.figdir = figdir
    Pweb.cachedir = cachedir
    doc.documentationmode = docmode
    doc.storeresults = cache

    if figformat is not None:
        doc.formatdict['figfmt'] = figformat
        doc.formatdict['savedformats'] = [figformat]

    #Returning globals
    try:
        doc.weave()
        if returnglobals:
        #Get the calling scope and return results to its globals
        #this way you can modify the weaved variables from repl
            _returnglobals()
    except Exception as inst:
        sys.stderr.write('%s\n%s\n' % (type(inst), inst.args))
        #Return varibles used this far if there is an exception
        if returnglobals:
           _returnglobals()

def _returnglobals():
    """Inspect stack to get the scope of the terminal/script calling pweave function"""
    if hasattr(sys,'_getframe'):
        caller = inspect.stack()[2][0]
        caller.f_globals.update(Pweb.globals)
    if not hasattr(sys,'_getframe'):
        print('%s\n%s\n' % ("Can't return globals" ,"Start Ironpython with ipy -X:Frames if you wan't this to work"))

def ptangle(file):
    """Tangles a noweb file i.e. extracts code from code chunks to a .py file
    
    :param file: ``string`` the pweave document containing the code
    """
    doc = Pweb(file)
    doc.tangle()

class PwebReader(object):
    """Reads and parses Pweb documents"""

    def __init__(self, file = None):
        self.source = file

    def read(self):
        codefile = open(self.source, 'r')
        #Prepend "@\n" to code in order to
        #ChunksToDict to work with the first text chunk
        code = "@\n" + codefile.read()
        codefile.close()
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
        return(self.parsed)

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
        defaults = Pweb.defaultoptions.copy()

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

class PwebProcessor(object):
    """Runs code from parsed Pweave documents"""

    def __init__(self, parsed, source, mode, formatdict):
        self.parsed = parsed
        self.source = source
        self.documentationmode = mode
        self._stdout = sys.stdout
        self.formatdict = formatdict

    def _basename(self):
        return(re.split("\.+[^\.]+$", self.source)[0])
        
    def run(self):
        #Create directory for figures
        if not os.path.isdir(Pweb.figdir):
            os.mkdir(Pweb.figdir)

        #Documentation mode uses results from previous  executions
        #so that compilation is fast if you only work on doc chunks
        if self.documentationmode:
           success = self._getoldresults()
           if success:
                return
           else:
               sys.stderr.write("DOCUMENTATION MODE ERROR:\nCan't find stored results, running the code and caching results for the next documentation mode run\n")
               Pweb.storeresults = True
        exec("import sys\nsys.path.append('.')", Pweb.globals)
        self.executed = map(self._runcode, self.parsed)
        self.isexecuted = True
        if Pweb.storeresults:
            self.store(self.executed)

    def getresults(self):
        return(self.executed)

    def store(self, data):
        """A method used to pickle stuff for persistence"""
        if not os.path.isdir(Pweb.cachedir):
            os.mkdir(Pweb.cachedir)
        name = Pweb.cachedir + '/' + self._basename() + '.pkl'
        f = open(name, 'wb')
        pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)
        f.close()

    def _runcode(self, chunk):
        """Execute code from a code chunk based on options"""
        if chunk['type'] != 'doc' and chunk['type'] !='code':
            return(chunk)

        #Make function to dispatch based on the type
        #Execute a function from a list of functions
        #Store builtin functions in a class and add them to a list
        #when the object initialises or just use getattr?

		#List functions from a class:
        #filter(lambda x : not x.startswith('_')   ,dir(pweave.PwebFormatters))

		#Users can then append their own functions
        #filter(lambda x: x.func_name=='f', a)[0](10)

        if chunk['type'] == 'doc':
            chunk['content'] = self.loadinline(chunk['content'])
            return(chunk)

        #Settings for figures, matplotlib and sho
        #if chunk['width'] is None:
        #        chunk['width'] = self.formatdict['width']
        
        if Pweb.usematplotlib:
            if not Pweb._mpl_imported:
                import matplotlib
                matplotlib.use('Agg')
                #matplotlib.rcParams.update(self.rcParams)
            import matplotlib.pyplot as plt
            import matplotlib
            Pweb._mpl_imported = True

            #['figure.figsize'] = (6, 4)
            #matplotlib.rcParams['figure.dpi'] = 200
        #Sho should be added in users code if it is used
        #if self.usesho:
        #    sys.path.append("C:\Program Files (x86)\Sho 2.0 for .NET 4\Sho")
        #    from sho import *
        if chunk['type'] == 'code':
            sys.stdout.write("Processing chunk %(number)s named %(name)s\n" % chunk)

            if not chunk['evaluate']:
                chunk['result'] = ''
                return(chunk)
            if chunk['term']:
                #try to use term, if fail use exec whole chunk
                #term seems to fail on function definitions
                stdold = sys.stdout
                try:
                    chunk['result'] = self.loadterm(chunk['content'])
                except Exception as inst:
                    sys.stdout = stdold
                    sys.stderr.write('Failed to execute chunk in term mode executing with term = False instead\nThis can sometimes happen at least with function definitions even if there is no syntax error\nEXCEPTION :')
                    sys.stderr.write('%s\n%s\n' % (type(inst), inst.args))
                    chunk['result'] = self.loadstring(chunk['content'])
                    chunk['term'] = False
            else:
                    chunk['result'] = self.loadstring(chunk['content'])
        #After executing the code save the figure
        if chunk['fig']:
            chunk['figure'] = self.savefigs(chunk)                
        return(chunk)


    def savefigs(self, chunk):
        if chunk['name'] is None:
            prefix = self._basename() + '_figure' + str(chunk['number'])
        else:
            prefix = self._basename() + '_' + chunk['name']
        
        fignames = []

        if Pweb.usematplotlib:
            import matplotlib.pyplot as plt
            #Iterate over figures
            figs = plt.get_fignums()
            #print figs
            for i in figs:
                plt.figure(i)
                name = Pweb.figdir + '/' + prefix + "_" + str(i) + self.formatdict['figfmt']
                for format in self.formatdict['savedformats']:
                    plt.savefig(Pweb.figdir + '/' + prefix + "_" + str(i) + format)
                    plt.draw()
                fignames.append(name)
                #plt.clf()
                plt.close()

        if Pweb.usesho:
            from sho import saveplot
            figname = Pweb.figdir + '/' + prefix + self.formatdict['figfmt']
            saveplot(figname)
            fignames = [figname]

        return(fignames)

    def restore(self):
        """A method used to unpickle stuff"""
        name = Pweb.cachedir + '/' + self._basename() + '.pkl'
        if os.path.exists(name):
            f = open(name, 'rb')
            self._oldresults = pickle.load(f)
            f.close()
            return(True)
        else:
            return(False)

    def _basename(self):
        return(re.split("\.+[^\.]+$", self.source)[0])

    def _getoldresults(self):
        """Get the results of previous run for documentation mode"""
        success = self.restore()
        if not success:
            return(False)
        old = filter(lambda x: x['type']=='code', self._oldresults)
        executed = self.parsed
        for chunk in executed:
            if chunk['type']!='code' and chunk['type']!='doc':
                continue
            #No caching for inline code yet, just hide it
            if chunk['type'] is 'doc':
                chunk.update(self._hideinline(chunk))
                continue
            nbr = chunk['number']
            stored = filter(lambda x : x['number'] == nbr,  old)[0]
            if chunk['content'] != stored['content']:
                sys.stderr.write('WARNING: contents of chunk number %(number)s (name = %(name)s) have changed\n' % chunk)
            #print stored
            chunk.update(stored)
        self.executed = executed
        return(True)

    def loadstring(self, code):
        tmp = StringIO()
        sys.stdout = tmp
        compiled = compile(code, '<input>', 'exec')
        exec compiled in Pweb.globals
        result = "\n" + tmp.getvalue()
        tmp.close()
        sys.stdout = self._stdout
        return(result)

    def loadterm(self, chunk):
        #Write output to a StringIO object
        #loop trough the code lines
        statement = ""
        prompt = ">>>"
        chunkresult = "\n"
        block = chunk.lstrip().splitlines()

        for x in block:
            chunkresult += ('%s %s\n' % (prompt, x))
            statement += x + '\n'

            # Is the statement complete?
            compiled_statement = code.compile_command(statement)
            if compiled_statement is None:
                # No, not yet.
                prompt = "..."
                continue

            if prompt != '>>>':
                chunkresult += ('%s \n' % (prompt))

            tmp = StringIO()
            sys.stdout = tmp
            return_value = eval(compiled_statement, Pweb.globals)
            result = tmp.getvalue()
            if return_value is not None:
                result += repr(return_value)
            tmp.close()
            sys.stdout = self._stdout
            if result:
                chunkresult += result

            statement = ""
            prompt = ">>>"

        return(chunkresult)

    def loadinline(self, content):
        """Evaluate code from doc chunks using ERB markup"""
        #Flags don't work with ironpython
        splitted = re.split('(<%[\w\s\W]*?%>)', content)#, flags = re.S)
        #No inline code
        if len(splitted)<2:
            return(content)

        n = len(splitted)

        for i in range(n):
            elem = splitted[i]
            if not elem.startswith('<%'):
                continue
            if elem.startswith('<%='):
                code = elem.replace('<%=', '').replace('%>', '').lstrip()
                result = self.loadstring('print %s,' % code).replace('\n','', 1)
                splitted[i] = result
                continue
            if elem.startswith('<%'):
                code = elem.replace('<%', '').replace('%>', '').lstrip()
                result = self.loadstring('%s' % code).replace('\n','', 1)
                splitted[i] = result
        return(''.join(splitted))

    def _hideinline(self, chunk):
        """Hide inline code in doc mode"""
        splitted = re.split('<%[\w\s\W]*?%>', chunk['content'])
        chunk['content'] = ''.join(splitted)
        return(chunk)

class Pweb(object):
    """Processes a complete document and contains Pweave options"""

    #Shared across class instances
    chunkformatters = []
    chunkprocessors = []
    globals = {}

    #: Default options for code chunks
    defaultoptions = dict(echo = True,
                          results = 'verbatim',
                          fig = False,
                          include = True,
                          evaluate = True,
                          #width = None,
                          caption = False,
                          term = False,
                          name = None,
                          wrap = True)

    figdir = 'figures'
    cachedir = 'cache'
    usematplotlib = True
    usesho = False
    storeresults = True
    _mpl_imported = False

    def __init__(self, file = None):
        
        #: The source document
        self.source = file
        self.sink = None
        self.doctype = 'tex'
        self.parsed = None
        self.executed = None
        self.formatted = None
        self.isparsed = False
        self.isexecuted = False
        self.isformatted = False
        
        self.usesho = False
        #Pickle results for use with documentation mode
        self.documentationmode = False
        self.setformat(self.doctype)

    def setformat(self, doctype = 'tex', Formatter = None):
        #Formatters are needed  when the code is executed and formatted 
        if Formatter is not None:
            self.formatter = Formatter()
            return
        
        
        if doctype == 'tex':
            self.formatter = PwebTexFormatter()
        if doctype == 'rst':
            self.formatter = PwebRstFormatter()
        if doctype == 'pandoc':
            self.formatter = PwebPandocFormatter()
        if doctype == 'sphinx':
            self.formatter = PwebSphinxFormatter()
        if doctype == 'html':
            self.formatter = PwebHTMLFormatter()

    def updateformat(self, dict):
        self.formatter.formatdict(dict)

    def useminted(self):
         if self.doctype == 'tex':
            self.formatter.updateformatdict(
              dict(
                codestart = r'\begin{minted}[mathescape, fontsize=\footnotesize, xleftmargin=0.5em]{python}',
                codeend = '\end{minted}\n',
                outputstart = r'\begin{minted}[fontsize=\footnotesize, fontshape=sl, xleftmargin=0.5em, mathescape]{text}',
                outputend = '\end{minted}\n',
                termstart = r'\begin{minted}[fontsize=\footnotesize, xleftmargin=0.5em, mathescape]{python}',
                termend = '\end{minted}\n'))
    
    def parse(self):
        parser = PwebReader(self.source)
        parser.read()
        self.parsed = parser.getparsed()
        self.isparsed = True

    def run(self):
        runner = PwebProcessor(self.parsed, self.source, self.documentationmode, self.formatter.getformatdict())
        runner.run()
        self.executed = runner.getresults()
        self.isexecuted = True

    def format(self):
        if not self.isexecuted:
            self.run()
        self.formatter.setexecuted(self.executed)
        self.formatter.format()
        self.formatted =  self.formatter.getformatted()
        self.isformatted = True

    def write(self):
        if not self.isformatted:
            self.format()
        if self.sink is None:
            self.sink = self._basename() + '.' + self.formatter.getformatdict()['extension']
        f = open(self.sink, 'w')
        text = "".join(self.formatted)
      
        #splitted = text.split("\n")
        #result = ""
        #for line in splitted:
        #    result += formatters.wrapper(line, 75) + '\n'
        #    text = result
        f.write(text)
        f.close()
        sys.stdout.write('Pweaved %s to %s\n' % (self.source, self.sink))

    def _basename(self):
        return(re.split("\.+[^\.]+$", self.source)[0])

    def weave(self):
        self.parse()
        self.run()
        self.format()
        self.write()

    def tangle(self):
        self.parse()
        target = self._basename() + '.py'
        code = filter(lambda x : x['type'] == 'code', self.parsed)
        code = map(lambda x : x['content'], code)
        f = open(target, 'w')
        f.write('\n'.join(code))
        f.close()
        sys.stdout.write('Tangled code from %s to %s\n' % (self.source, target))

    def _getformatter(self, chunk):
        """Call code from pweave.formatters and user provided formatters
        allows overriding default options for doc and code chunks
        the function needs to return a string"""
        #Check if there are custom functions in Pweb.chunkformatter
        f = filter(lambda x: x.func_name==('format%(type)schunk' % chunk), Pweb.chunkformatters)
        if f:
            return(f[0](chunk))
        #Check built-in formatters from pweave.formatters
        if hasattr (formatters, ('format%(type)schunk' % chunk)):
            result = getattr(formatters, ('format%(type)schunk' % chunk))(chunk)
            return(result)
        #If formatter is not found
        if chunk['type'] == 'code' or chunk['type'] == 'doc':
            return(chunk)
        sys.stderr.write('UNKNOWN CHUNK TYPE: %s \n' % chunk['type'])
        return(None)

    
