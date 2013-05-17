import os
import sys
import re
from cStringIO import StringIO
import code
import inspect
from . import formatters
from formatters import *
from . import readers
import cPickle as pickle
import copy


class PwebProcessor(object):
    """Runs code from parsed Pweave documents"""

    def __init__(self, parsed, source, mode, formatdict):
        self.parsed = parsed
        self.source = source
        self.documentationmode = mode
        self._stdout = sys.stdout
        self.formatdict = formatdict
        self.pending_code = "" # Used for multichunk splits

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
               print "restoring" 
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
        return(copy.deepcopy(self.executed))

    def store(self, data):
        """A method used to pickle stuff for persistence"""
        if not os.path.isdir(Pweb.cachedir):
            os.mkdir(Pweb.cachedir)
        name = Pweb.cachedir + '/' + self._basename() + '.pkl'
        f = open(name, 'wb')
        pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)
        f.close()
        #print (len(data))
        #f = open(name, 'w')
        #f.write(json.dumps(data, indent=4, separators=(',', ': ')))
        #f.close()


    def _runcode(self, chunk):
        """Execute code from a code chunk based on options"""
        if chunk['type'] != 'doc' and chunk['type'] !='code':
            return(chunk)

        #Add defaultoptions to parsed options
        if chunk['type'] == 'code':
           defaults = Pweb.defaultoptions.copy()
           defaults.update(chunk["options"])
           chunk.update(defaults)
           del chunk['options']

         #Read the content from file or object
        if chunk.has_key("source"):
            source = chunk["source"]
            if os.path.isfile(source): 
                chunk["content"] = open(source, "r").read()  + chunk['content']
            else:
                chunk["content"] = self.loadstring("import inspect\nprint(inspect.getsource(%s))" % source) + chunk['content']


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

            #Handle code split across several chunks
            old_content = None
            if not chunk["complete"]:
                self.pending_code += chunk["content"]
                chunk['result'] = ''
                return(chunk)
            elif self.pending_code != "":
                old_content = chunk["content"]
                chunk["content"] = self.pending_code + old_content # Code from all pending chunks for running the code
                self.pending_code = ""

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
                    try:
                        sys.stderr.write('Executing in term mode:')
                        chunk['result'] = self.loadstring(chunk['content'])
                        chunk['term'] = False
                    except:
                        raise
            else:
                    chunk['result'] = self.loadstring(chunk['content'])
        #After executing the code save the figure
        if chunk['fig']:
            chunk['figure'] = self.savefigs(chunk)                
        
        if old_content != None:
            chunk['content'] = old_content # The code from current chunk for display

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
                plt.figure(i).set_size_inches(chunk['f_size'])
                #plt.figure(i).set_size_inches(4,4)

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
            #f = open(name, 'r')
            #self._oldresults= json.loads(f.read())
            #print(len(self._oldresults))
            #f.close()
            return(True)
        else:
            return(False)

    def _basename(self):
        return(re.split("\.+[^\.]+$", self.source)[0])

    def _getoldresults(self):
        """Get the results of previous run for documentation mode"""
        from pprint import pprint
        success = self.restore()
        if not success:
            return(False)

        executed = []

        n = len(self.parsed)

        for i in range(n):
            chunk = self.parsed[i]
            if chunk['type'] is not "code":
                executed.append(self._hideinline(chunk.copy()))
            else:
                executed.append(self._oldresults[i].copy())

        #old = filter(lambda x: x['type']=='code', self._oldresults)
        #executed = self.parsed
        #for chunk in executed:
        #    if chunk['type']!='code' and chunk['type']!='doc':
        #        continue
        #    #No caching for inline code yet, just hide it
        #    if chunk['type'] is 'doc':
        #        chunk.update(self._hideinline(chunk))
        #        continue
        #    nbr = chunk['number']
        #    stored = filter(lambda x : x['number'] == nbr,  old)[0]
        #    if chunk['content'] != stored['content']:
        #        sys.stderr.write('WARNING: contents of chunk number %(number)s (name = %(name)s) have changed\n' % chunk)
        #    print stored
        #    chunk.update(stored)
            
        self.executed = executed
        #pprint(self.executed)
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

class PwebIPythonProcessor(PwebProcessor):
    """Runs code from parsed Pweave documents"""

    def __init__(self, parsed, source, mode, formatdict):
        PwebProcessor.__init__(self, parsed, source, mode, formatdict)
        import IPython
        x = IPython.core.interactiveshell.InteractiveShell()
        self.IPy = x.get_ipython()
        self.prompt_count = 1

    def loadstring(self, code):
        tmp = StringIO()
        sys.stdout = tmp
        #compiled = compile(code, '<input>', 'exec')
        #exec compiled in Pweb.globals
        self.IPy.run_cell(code)
        result = "\n" + tmp.getvalue()
        tmp.close()
        sys.stdout = self._stdout
        return(result)

    def loadterm(self, chunk):
        #Write output to a StringIO object
        #loop trough the code lines
        statement = ""
        prompt = "In [%i]:" % self.prompt_count
        chunkresult = "\n"
        block = chunk.lstrip().splitlines()

        for x in block:
            chunkresult += ('\n%s %s\n' % (prompt, x))
            statement += x + '\n'

            # Is the statement complete?
            compiled_statement = code.compile_command(statement)
            if compiled_statement is None:
                # No, not yet.
                prompt = "..."
                continue

            if not prompt.startswith('In ['):
                chunkresult += ('%s \n' % (prompt))

            tmp = StringIO()
            sys.stdout = tmp
            #return_value = eval(compiled_statement, Pweb.globals)
            self.IPy.run_code(compiled_statement)
            result = tmp.getvalue()
            #if return_value is not None:
            #    result += repr(return_value)
            tmp.close()
            sys.stdout = self._stdout
            if result:
                chunkresult += ("Out[%i]: " % self.prompt_count) + result.rstrip()

            statement = ""
            self.prompt_count +=1
            prompt = 'In [%i]:' % self.prompt_count

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

class Pweb(object):
    """Processes a complete document
    
    :param file: ``string`` name of the input document.
    :param format: ``string`` output format from supported formats. See: http://mpastell.com/pweave/formats.html
    """

    #Shared across class instances
    chunkformatters = []
    chunkprocessors = []
    
    #: Globals dictionary used when evaluating code
    globals = {}

    #: Default options for chunks
    defaultoptions = dict(echo = True,
                          results = 'verbatim',
                          fig = True,
                          include = True,
                          evaluate = True,
                          #width = None,
                          caption = False,
                          term = False,
                          name = None,
                          wrap = False,
                          f_pos = "htpb",
                          f_size = (8, 6),
                          f_env = None,
                          complete = True
                          )
    
    #: Pweave figure directory
    figdir = 'figures'
    
    #: Pweave cache directory
    cachedir = 'cache'
    
    #: Use plots? 
    usematplotlib = True
    

    usesho = False
    storeresults = False
    _mpl_imported = False

    def __init__(self, file = None, format = "tex"):
        
        #The source document
        self.source = file
        self.sink = None
        self.doctype = format
        self.parsed = None
        self.executed = None
        self.formatted = None
        self.isparsed = False
        self.isexecuted = False
        self.isformatted = False
        
        self.usesho = False
        
        #: Use documentation mode?
        self.documentationmode = False

        self.Reader = readers.PwebReader

        self.setformat(self.doctype)

    def setformat(self, doctype = 'tex', Formatter = None):
        """Set output format for the document
        
        :param doctype: ``string`` output format from supported formats. See: http://mpastell.com/pweave/formats.html
        :param Formatter: Formatter class, can be used to specify custom formatters. See: http://mpastell.com/pweave/subclassing.html
        
        """
        #Formatters are needed  when the code is executed and formatted 
        if Formatter is not None:
            self.formatter = Formatter(self.source)
            return
        #Get formatter class from available formatters
        try:
            self.formatter = PwebFormats.formats[doctype]['class'](self.source)
        except KeyError as e:
            raise Exception("Pweave: Unknown output format")
            
    def setreader(self, Reader = readers.PwebReader):
        """Set class reading for reading documents, 
        readers can be used to implement different input markups""" 
        if type(Reader) == str:
            self.Reader = readers.PwebReaders.listformats[Reader]['class']
        else:
            self.Reader = Reader

    def getformat(self):
        """Get current format dictionary. See: http://mpastell.com/pweave/customizing.html"""
        return(self.formatter.formatdict)
              
    def updateformat(self, dict):
        """Update existing format, See: http://mpastell.com/pweave/customizing.html"""
        self.formatter.formatdict.update(dict)
    
    def parse(self, string = None, basename = "string_input"):
        """Parse document""" 
        if string is None:
            parser = self.Reader(file = self.source)
        else:
            parser = self.Reader(string = string)
            self.source = basename
        parser.parse()
        self.parsed = parser.getparsed()
        self.isparsed = True

    def run(self):
        """Execute code in the document"""
        #runner = PwebProcessor(copy.deepcopy(self.parsed), self.source, self.documentationmode, self.formatter.getformatdict())
        runner = PwebIPythonProcessor(copy.deepcopy(self.parsed), self.source, self.documentationmode, self.formatter.getformatdict())
        runner.run()
        self.executed = runner.getresults()
        self.isexecuted = True

    def format(self):
        """Format the code for writing""" 
        if not self.isexecuted:
            self.run()
        self.formatter.setexecuted(copy.deepcopy(self.executed))
        self.formatter.format()
        self.formatted =  self.formatter.getformatted()
        self.isformatted = True

    def write(self, action = "Pweaved"):
        """Write formatted code to file"""
        if not self.isformatted:
            self.format()
        if self.sink is None:
            self.sink = self._basename() + '.' + self.formatter.getformatdict()['extension']
        f = open(self.sink, 'w')
        f.write(self.formatted.replace("\r", ""))
        f.close()
        sys.stdout.write('%s %s to %s\n' % (action, self.source, self.sink))

    def _basename(self):
        return(re.split("\.+[^\.]+$", self.source)[0])

    def weave(self):
        """Weave the document, equals -> parse, run, format, write"""
        if not self.isparsed:
            self.parse()
        self.run()
        self.format()
        self.write()

    def tangle(self):
        """Tangle the document"""
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
  