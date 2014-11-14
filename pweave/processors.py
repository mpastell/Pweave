#Processors that execute code from code chunks
from __future__ import print_function, division, absolute_import

import sys
import os
import re
import os
import io
try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO
import copy
import code
try:
    import cPickle as pickle
except ImportError:
    import pickle
from subprocess import Popen, PIPE
from .config import *

class PwebProcessor(object):
    """Runs code from parsed Pweave documents"""

    def __init__(self, parsed, source, mode, formatdict):
        self.parsed = parsed
        self.source = source
        self.documentationmode = mode
        self.cwd = os.path.dirname(os.path.abspath(source))
        self.basename = os.path.basename(os.path.abspath(source)).split(".")[0]
        self._stdout = sys.stdout
        self.formatdict = formatdict
        self.pending_code = "" # Used for multichunk splits
        self._mpl_imported = False


    def run(self):
        #Create directory for figures
        if not os.path.isdir(rcParams["figdir"]):
            os.mkdir(rcParams["figdir"])

        #Documentation mode uses results from previous  executions
        #so that compilation is fast if you only work on doc chunks
        if self.documentationmode:
           success = self._getoldresults()
           if success:
               print("Restoring cached results")
               return
           else:
               sys.stderr.write("DOCUMENTATION MODE ERROR:\nCan't find stored results, running the code and caching results for the next documentation mode run\n")
               rcParams["storeresults"] = True
        exec("import sys\nsys.path.append('.')", PwebProcessorGlobals.globals)
        self.executed = list(map(self._runcode, self.parsed))
        self.isexecuted = True
        if rcParams["storeresults"]:
            self.store(self.executed)

    def getresults(self):
        return(copy.deepcopy(self.executed))

    def store(self, data):
        """A method used to pickle stuff for persistence"""
        cachedir = os.path.join(self.cwd, rcParams["cachedir"])
        if not os.path.isdir(cachedir):
            os.mkdir(cachedir)

        name = cachedir + "/" + self.basename + ".pkl"
        f = open(name, 'wb')
        pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)
        f.close()


    def restore(self):
        """A method used to unpickle stuff"""
        cachedir = os.path.join(self.cwd, rcParams["cachedir"])
        name = cachedir + "/" + self.basename + ".pkl"

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


    def _runcode(self, chunk):
        """Execute code from a code chunk based on options"""
        if chunk['type'] != 'doc' and chunk['type'] !='code':
            return(chunk)

        #Add defaultoptions to parsed options
        if chunk['type'] == 'code':
           defaults = rcParams["chunk"]["defaultoptions"].copy()
           defaults.update(chunk["options"])
           chunk.update(defaults)
           del chunk['options']

         #Read the content from file or object
        if 'source' in chunk:
            source = chunk["source"]
            if os.path.isfile(source):
                chunk["content"] = "\n" + io.open(source, "r", encoding='utf-8').read().rstrip() + "\n"  + chunk['content']
            else:
                chunk_text = chunk["content"] #Get the text from chunk
                module_text = self.loadstring("import inspect\nprint(inspect.getsource(%s))" % source)  #Get the module source using inspect
                chunk["content"] = module_text.rstrip()
                if chunk_text.strip() != "":
                    chunk["content"] += "\n" + chunk_text



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

        #Engines different from python, shell commands for now
        if chunk['engine'] == "shell":
            sys.stdout.write("Processing chunk %(number)s named %(name)s from line %(start_line)s\n" % chunk)
            chunk['result']  = self.load_shell(chunk)

            #chunk['term'] = True
            return(chunk)

        #Settings for figures, matplotlib and sho
        #if chunk['width'] is None:
        #        chunk['width'] = self.formatdict['width']

        if rcParams["usematplotlib"]:
            if not self._mpl_imported:
                import matplotlib
                matplotlib.use('Agg')
                #matplotlib.rcParams.update(self.rcParams)
            import matplotlib.pyplot as plt
            import matplotlib
            self._mpl_imported = True

            #['figure.figsize'] = (6, 4)
            #matplotlib.rcParams['figure.dpi'] = 200
        #Sho should be added in users code if it is used
        #if self.usesho:
        #    sys.path.append("C:\Program Files (x86)\Sho 2.0 for .NET 4\Sho")
        #    from sho import *
        if chunk['type'] == 'code':
            sys.stdout.write("Processing chunk %(number)s named %(name)s from line %(start_line)s\n" % chunk)


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
                except Exception as e:
                    sys.stdout = stdold
                    sys.stderr.write("  Exception:\n")
                    sys.stderr.write("  " + str(e) + "\n")
                    sys.stderr.write("  Error messages will be included in output document\n" % chunk)
                    chunk["result"] = "%s\n\n%s\n%s" % (chunk["content"], type(e), e)
            else:
                try:
                    chunk['result'] = self.loadstring(chunk['content'])
                except Exception as e:
                    sys.stderr.write("  Exception:\n")
                    sys.stderr.write("  " + str(e) + "\n")
                    sys.stderr.write("  Error messages will be included in output document\n" % chunk)
                    chunk["result"] = "\n%s\n%s" % (type(e), e)






    #After executing the code save the figure
        if chunk['fig']:
            chunk['figure'] = self.savefigs(chunk)

        if old_content is not None:
            chunk['content'] = old_content # The code from current chunk for display

        return(chunk)


    def savefigs(self, chunk):
        if chunk['name'] is None:
            prefix = self.basename + '_figure' + str(chunk['number'])
        else:
            prefix = self.basename + '_' + chunk['name']

        figdir = os.path.join(self.cwd, rcParams["figdir"])
        if not os.path.isdir(figdir):
            os.mkdir(figdir)

        fignames = []

        if rcParams["usematplotlib"]:
            import matplotlib.pyplot as plt
            #Iterate over figures
            figs = plt.get_fignums()
            #print figs
            for i in figs:
                plt.figure(i)
                plt.figure(i).set_size_inches(chunk['f_size'])
                if not chunk["f_spines"]:
                    axes = plt.figure(i).axes
                    for ax in axes:
                        ax.spines['right'].set_visible(False)
                        ax.spines['top'].set_visible(False)
                        ax.yaxis.set_ticks_position('left')
                        ax.xaxis.set_ticks_position('bottom')

                name = rcParams["figdir"] + "/" + prefix + "_" + str(i) + self.formatdict['figfmt']

                for format in self.formatdict['savedformats']:
                    f_name = os.path.join(self.cwd, rcParams["figdir"], prefix + "_" + str(i)) + format
                    plt.savefig(f_name)

                    plt.draw()
                fignames.append(name)
                plt.close()

        return(fignames)



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
            if chunk['type'] != "code":
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

    #Run shell commands from code chunks
    def load_shell(self, chunk):
        if chunk['evaluate']:
            lines = chunk['content'].lstrip().splitlines()
            result = "\n"
            for line in lines:
                command = line.split()
                try:
                    cmd = Popen(command, stdout = PIPE)
                    content = cmd.communicate()[0].replace("\r", "").encode('utf-8') + "\n"
                except Exception as e:
                    content = "Pweave ERROR can't execute shell command:\n %s\n" % command
                    content += str(e)
                    sys.stdout.write("  Pweave ERROR can't execute shell command:\n %s\n" % line)
                    print(str(e))
                if chunk['term']:
                    result += "$ %s\n" % line
                result += content
        else:
            result = ""

        return(result)


    def loadstring(self, code, scope=PwebProcessorGlobals.globals):
        tmp = StringIO()
        sys.stdout = tmp
        compiled = compile(code, "chunk", 'exec')
        exec(compiled, scope)
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
            compiled_statement = code.compile_command(statement, self.source)
            if compiled_statement is None:
                # No, not yet.
                prompt = "..."
                continue

            if prompt != '>>>':
                chunkresult += ('%s \n' % (prompt))

            tmp = StringIO()
            sys.stdout = tmp
            return_value = eval(compiled_statement, PwebProcessorGlobals.globals)
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
                result = self.loadstring('print(%s),' % code).replace('\n','', 1)
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
        #exec compiled in PwebProcessorGlobals.globals
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
            #return_value = eval(compiled_statement, PwebProcessorGlobals.globals)
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

class PwebProcessors(object):
    """Lists available input formats"""
    formats = {'python' : {'class' : PwebProcessor, 'description' :  'Python shell'},
               'ipython' : {'class' : PwebIPythonProcessor, 'description' :  'IPython shell'}
               }

    @classmethod
    def shortformats(cls):
        fmtstring = ""
        names = list(cls.formats.keys())
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
        print("\nPweave supported shells:\n")
        print(cls.getformats())
        print("More info: http://mpastell.com/pweave/ \n")



