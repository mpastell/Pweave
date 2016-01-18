# Processors that execute code from code chunks
from __future__ import print_function, division, absolute_import
import json
import sys
import re
import os
import io
from subprocess import Popen, PIPE
import shutil
import traceback


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
try:
    from subprocess import TimeoutExpired
except ImportError:
    pass
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
        self.pending_code = ""  # Used for multichunk splits
        self.init_matplotlib()

    def run(self):
        # Create directory for figures
        if not os.path.isdir(rcParams["figdir"]):
            os.mkdir(rcParams["figdir"])

        # Documentation mode uses results from previous  executions
        # so that compilation is fast if you only work on doc chunks
        if self.documentationmode:
            success = self._getoldresults()
            if success:
                print("Restoring cached results")
                return
            else:
                sys.stderr.write(
                    "DOCUMENTATION MODE ERROR:\nCan't find stored results, running the code and caching results for the next documentation mode run\n")
                rcParams["storeresults"] = True
        exec("import sys\nsys.path.append('.')", PwebProcessorGlobals.globals)
        self.executed = list(map(self._runcode, self.parsed))
        self.isexecuted = True
        if rcParams["storeresults"]:
            self.store(self.executed)

    def getresults(self):
        return copy.deepcopy(self.executed)

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
            # f = open(name, 'r')
            # self._oldresults= json.loads(f.read())
            # print(len(self._oldresults))
            #f.close()
            return True
        else:
            return False

    def _runcode(self, chunk):
        """Execute code from a code chunk based on options"""
        if chunk['type'] != 'doc' and chunk['type'] != 'code':
            return chunk

        # Add defaultoptions to parsed options
        if chunk['type'] == 'code':
            defaults = rcParams["chunk"]["defaultoptions"].copy()
            defaults.update(chunk["options"])
            chunk.update(defaults)
            del chunk['options']

            # Read the content from file or object
        if 'source' in chunk:
            source = chunk["source"]
            if os.path.isfile(source):
                chunk["content"] = "\n" + io.open(source, "r", encoding='utf-8').read().rstrip() + "\n" + chunk[
                    'content']
            else:
                chunk_text = chunk["content"]  # Get the text from chunk
                module_text = self.loadstring(
                    "import inspect\nprint(inspect.getsource(%s))" % source)  # Get the module source using inspect
                chunk["content"] = module_text.rstrip()
                if chunk_text.strip() != "":
                    chunk["content"] += "\n" + chunk_text

        if chunk['type'] == 'doc':
            chunk['content'] = self.loadinline(chunk['content'])
            return chunk

        # Engines different from python, shell commands for now
        if chunk['engine'] == "shell":
            sys.stdout.write("Processing chunk %(number)s named %(name)s from line %(start_line)s\n" % chunk)
            chunk['result'] = self.load_shell(chunk)

            #chunk['term'] = True
            return chunk

        if chunk['type'] == 'code':
            sys.stdout.write("Processing chunk %(number)s named %(name)s from line %(start_line)s\n" % chunk)

            old_content = None
            if not chunk["complete"]:
                self.pending_code += chunk["content"]
                chunk['result'] = ''
                return chunk
            elif self.pending_code != "":
                old_content = chunk["content"]
                chunk["content"] = self.pending_code + old_content  # Code from all pending chunks for running the code
                self.pending_code = ""

            if not chunk['evaluate']:
                chunk['result'] = ''
                return chunk
            if chunk['term']:
                #try to use term, if fail use exec whole chunk
                #term seems to fail on function definitions
                stdold = sys.stdout
                try:
                    chunk['result'] = self.loadterm(chunk['content'], chunk=chunk)
                except Exception as e:
                    sys.stdout = stdold
                    sys.stderr.write("  Exception:\n")
                    sys.stderr.write("  " + str(e) + "\n")
                    sys.stderr.write("  Error messages will be included in output document\n" % chunk)
                    chunk["result"] = "%s\n\n%s\n%s" % (chunk["content"], type(e), e)
            else:
                try:
                    chunk['result'] = self.loadstring(chunk['content'], chunk=chunk)
                except Exception as e:
                    sys.stderr.write("  Exception:\n")
                    sys.stderr.write("  " + str(e) + "\n")
                    sys.stderr.write("  Error messages will be included in output document\n" % chunk)
                    chunk["result"] = "\n%s\n%s" % (type(e), e)

        #After executing the code save the figure
        if chunk['fig']:
            chunk['figure'] = self.savefigs(chunk)

        if old_content is not None:
            chunk['content'] = old_content  # The code from current chunk for display

        return chunk

    def init_matplotlib(self):
        if rcParams["usematplotlib"]:
            import matplotlib

            matplotlib.use('Agg')
            import matplotlib.pyplot as plt

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
            # Iterate over figures
            figs = plt.get_fignums()
            # print figs
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

        return fignames

    def _getoldresults(self):
        """Get the results of previous run for documentation mode"""

        success = self.restore()
        if not success:
            return False

        executed = []

        n = len(self.parsed)

        for i in range(n):
            chunk = self.parsed[i]
            if chunk['type'] != "code":
                executed.append(self._hideinline(chunk.copy()))
            else:
                executed.append(self._oldresults[i].copy())

        self.executed = executed
        return True

    def load_shell(self, chunk):
        """Run shell commands from code chunks"""
        if chunk['evaluate']:
            lines = chunk['content'].lstrip().splitlines()
            result = "\n"
            for line in lines:
                command = line.split()
                major, minor = sys.version_info[:2]
                cmd = Popen(command, stdout=PIPE)
                if major == 2 or minor < 3:  # Python 2 doesn't have timeout for subprocess
                    try:
                        content = cmd.communicate()[0].decode('utf-8').replace("\r", "") + "\n"
                    except Exception as e:
                        content = "Pweave ERROR can't execute shell command:\n %s\n" % command
                        content += str(e)
                        sys.stdout.write("  Pweave ERROR can't execute shell command:\n %s\n" % line)
                        print(str(e))
                else:
                    try:
                        content = cmd.communicate(timeout=10)[0].decode('utf-8').replace("\r", "") + "\n"
                    except TimeoutExpired:
                        cmd.kill()
                        content, errs = cmd.communicate()

                if chunk['term']:
                    result += "$ %s\n" % line
                result += content
        else:
            result = ""

        return result

    def loadstring(self, code, chunk=None, scope=PwebProcessorGlobals.globals):
        tmp = StringIO()
        sys.stdout = tmp
        compiled = compile(code, "chunk", 'exec')
        exec(compiled, scope)
        result = "\n" + tmp.getvalue()
        tmp.close()
        sys.stdout = self._stdout
        return result

    def loadterm(self, code_string, chunk=None):
        if chunk is None:
            source = self.source

        else:
            source = '< chunk {no} named {name} >'.format(no=chunk.get('number'),
                                                          name=chunk.get('name'),
                                                          source=self.source)
        emulator = self.ConsoleEmulator(PwebProcessorGlobals.globals,
                                        source)
        emulator.typeLines(code_string.lstrip().splitlines())
        return emulator.getOutput()

    def loadinline(self, content):
        """Evaluate code from doc chunks using ERB markup"""
        # Flags don't work with ironpython
        splitted = re.split('(<%[\w\s\W]*?%>)', content)  # , flags = re.S)
        # No inline code
        if len(splitted) < 2:
            return content

        n = len(splitted)

        for i in range(n):
            elem = splitted[i]
            if not elem.startswith('<%'):
                continue
            if elem.startswith('<%='):
                code_str = elem.replace('<%=', '').replace('%>', '').lstrip()
                result = self.loadstring(self.add_echo(code_str)).strip()
                splitted[i] = result
                continue
            if elem.startswith('<%'):
                code_str = elem.replace('<%', '').replace('%>', '').lstrip()
                result = self.loadstring(code_str).strip()
                splitted[i] = result
        return ''.join(splitted)

    def add_echo(self, code_str):
        return 'print(%s),' % code_str

    def _hideinline(self, chunk):
        """Hide inline code in doc mode"""
        splitted = re.split('<%[\w\s\W]*?%>', chunk['content'])
        chunk['content'] = ''.join(splitted)
        return chunk


    class ConsoleEmulator(object):
        def __init__(self, globals, source):
            self.__statement = []
            self.__chunkResult = "\n"
            self.__compiled = None
            self.__source = source
            self.__globals = globals
            self._probeTracebackSkip()

        def _probeTracebackSkip(self):
            try:
                eval(code.compile_command('raise Exception\n'))

            except Exception:
                _, _, eTb = sys.exc_info()
                self.__skipTb = len(traceback.extract_tb(eTb)) - 1

        def typeLines(self, block):
            for line in block:
                self.typeLine(line)

            if self._isStatementWaiting():
                self.typeLine('')

        def getOutput(self):
            return self.__chunkResult

        def typeLine(self, line):
            self._enterLine(line)
            compiled = self._compileStatement()
            if line == '' or self._isOneLineStatement():
                self._tryToProcessStatement(compiled)

        def _tryToProcessStatement(self, compiledStatement):
            if compiledStatement is not None:
                self._executeStatement(compiledStatement)
                self._forgetStatement()

        def _enterLine(self, line):
            self.__statement.append(line)
            self.__chunkResult += '{} {}\n'.format(self._getPrompt(), line)

        def _getPrompt(self):
            return '>>>' if self._isOneLineStatement() else '...'

        def _compileStatement(self):
            try:
                return code.compile_command('\n'.join(self.__statement) + '\n',
                                            self.__source)
            except SyntaxError:
                self.__chunkResult += self._getSyntaxError()
                self._forgetStatement()

        def _isOneLineStatement(self):
            return len(self.__statement) == 1

        def _isStatementWaiting(self):
            return self.__statement != []

        def _forgetStatement(self):
            self.__statement = []

        def _getRedirectedOutput(self):
            out = StringIO()
            sys.stdout = out
            sys.stderr = out
            def displayhook(obj=None):
                if obj is not None:
                    out.write('{!r}\n'.format(obj))

            sys.displayhook = displayhook
            return out

        def _executeStatement(self, statement):
            with ProtectStdStreams():
                out = self._getRedirectedOutput()
                try:
                    eval(statement,  self.__globals)

                except Exception:
                    out.write('Traceback (most recent call last):\n' \
                              + self._getExceptionTraceback())

            self.__chunkResult += out.getvalue()
            out.close()

        def _getSyntaxError(self):
            eType, eValue, _ = sys.exc_info()
            return ''.join(traceback.format_exception_only(eType, eValue))

        def _getExceptionTraceback(self):
            eType, eValue, eTb = sys.exc_info()
            skip = self.__skipTb
            result = traceback.format_list(traceback.extract_tb(eTb)[skip:]) \
                   + traceback.format_exception_only(eType, eValue)
            return ''.join(result)

class PwebSubProcessor(PwebProcessor):
    """Runs code in external Python shell using subprocess.Popen"""

    def __init__(self, parsed, source, mode, formatdict):
        err_file = open(os.path.dirname(os.path.abspath(source)) + "/epython_stderr.log", "wt")
        shell = rcParams["shell_path"]
        self.shell = Popen([shell, "-i", "-u"], stdin=PIPE, stdout=PIPE, stderr=err_file)
        PwebProcessor.__init__(self, parsed, source, mode, formatdict)
        self.run_string("__pweave_data__ = {}\n")
        self.send_data({"rcParams": rcParams, "cwd": self.cwd, "formatdict": self.formatdict})
        self.inline_count = 1  # Count inline code blocks

    def getresults(self):
        results, errors = self.shell.communicate()
        #print(results.decode('utf-8'))
        import bs4

        result_soup = bs4.BeautifulSoup(results.decode("utf-8"), "html.parser")

        for chunk in self.executed:
            if chunk["type"] == "doc":
                chunk_soup = bs4.BeautifulSoup(chunk["content"], "html.parser")
                inline_results = chunk_soup.find_all("inlineresult")
                if inline_results:
                    for inline_result in inline_results:
                        # First and last character are extra newlines
                        inline_result.string = result_soup.find(id=inline_result["id"]).text.replace("\r", "")[1:-1]
                        inline_result.unwrap()
                        chunk["content"] = chunk_soup.text

            elif chunk["type"] == "code":
                r = result_soup.find(id="results%i" % chunk["number"])
                if r is not None:  # chunks with continue True will not generate results
                    chunk["result"] = r.text
                else:
                    chunk["result"] = ""
                self.get_figures(chunk, result_soup)
            else:
                pass  # Other possible chunks like shell

        return copy.deepcopy(self.executed)

    def get_figures(self, chunk, result_soup):
        figs = result_soup.find(id="figs%i" % chunk["number"])
        if figs:
            chunk["figure"] = json.loads(figs.text)
        else:
            chunk["figure"] = []


    def insert_start_tag(self, chunk_id=0, chunk_type="term", id_prefix="results"):
        self.run_string("""print('<chunk id="%s%i" type="%s">')""" % (id_prefix, chunk_id, chunk_type))

    def insert_close_tag(self):
        self.run_string('print("</chunk>")')

    def run_string(self, code_string):
        self.shell.stdin.write(("\n" + code_string + "\n").encode('utf-8'))

    def loadstring(self, code_str, chunk=None, scope=None):
        self.insert_start_tag(chunk_type="block", chunk_id=chunk["number"])
        self.send_data({"chunk": chunk})
        self.run_string('exec(__pweave_data__["chunk"]["content"], globals(), locals())')
        self.insert_close_tag()

    def loadterm(self, code_str, chunk=None):
        code_str = code_str.replace("\r\n", "\n") + "\n"
        lines = code_str.lstrip().split("\n")

        n = len(lines) - 1
        block = ""

        self.insert_start_tag(chunk_type="term", chunk_id=chunk["number"])
        for i in range(n):
            if lines[i + 1].startswith(' '):
                block += '%s\n' % lines[i]
            elif block != "":
                block += '%s\n' % lines[i]
                self.run_string('print(""">>> %s""")' % self.terminalize(block))
                self.run_string('%s' % block)
                block = ""
            else:
                self.run_string('print(""">>> %s""")' % lines[i])
                self.run_string('%s' % lines[i])

        self.insert_close_tag()

    def terminalize(self, code_str):
        lines = code_str.split('\n')
        for i in range(len(lines)):
            if lines[i].startswith(' ') or lines[i] == '':
                lines[i] = '... ' + lines[i]

        return '\n'.join(lines)

    def loadinline(self, content):
        """Evaluate code from doc chunks using ERB markup"""
        # Flags don't work with ironpython
        splitted = re.split('(<%[\w\s\W]*?%>)', content)  # , flags = re.S)
        # No inline code
        if len(splitted) < 2:
            return content

        n = len(splitted)

        for i in range(n):
            elem = splitted[i]

            if not elem.startswith("<%"):
                continue
            self.insert_start_tag(self.inline_count, "inline", id_prefix="inlineresult")
            if elem.startswith('<%='):
                code_str = elem.replace('<%=', '').replace('%>', '').lstrip()
                self.run_inline_eval(code_str)
                result = '<inlineresult id="inlineresult%i" class="eval"></inlineresult>' % self.inline_count
            elif elem.startswith('<%'):
                code_str = elem.replace('<%', '').replace('%>', '').lstrip()
                self.run_inline_exec(code_str)
                result = '<inlineresult id="inlineresult%i" class="exec"></inlineresult>' % self.inline_count

            splitted[i] = result

            self.insert_close_tag()
            self.inline_count += 1

        return ''.join(splitted)

    def run_inline_eval(self, code_str):
        self.run_string(code_str)

    def run_inline_exec(self, code_str):
        self.send_data({"inlinechunk": code_str})
        self.run_string("exec(__pweave_data__['inlinechunk'])")

    def send_data(self, var_dict):
        """Send data to Python subprocess, contents of dictionary var_dict will be added to
         `__pweave_data__` dictionary in the subprocess"""

        send_data = StringIO(str(var_dict)).getvalue()
        self.run_string("__pweave_data__.update(%s)" % send_data)

    def var_to_string(self, var_dict):
        tmp = StringIO()
        sys.stdout = tmp
        scope = var_dict
        compiled = compile('print(%(var)s)' % var_dict, "chunk", 'exec')
        exec(compiled, scope)
        result = tmp.getvalue()
        tmp.close()
        sys.stdout = self._stdout
        return result

    def savefigs(self, chunk):
        if chunk['name'] is None:
            prefix = self.basename + '_figure' + str(chunk['number'])
        else:
            prefix = self.basename + '_' + chunk['name']

        figdir = os.path.join(self.cwd, rcParams["figdir"])
        if not os.path.isdir(figdir):
            os.mkdir(figdir)

        self.send_data({"figdir": figdir, "prefix": prefix})

        from . import subsnippets

        self.run_string(subsnippets.savefigs)

    def init_matplotlib(self):
        if rcParams["usematplotlib"]:
            self.run_string("\nimport matplotlib\nmatplotlib.use('Agg')\nimport matplotlib.pyplot as plt\n")


class OctaveProcessor(PwebSubProcessor):

    def __init__(self, parsed, source, mode, formatdict):
        err_file = open(os.path.dirname(os.path.abspath(source)) + "/octave_stderr.log", "wt")
        shell = "octave"
        #shell = rcParams["shell_path"]

        rcParams["chunk"]["defaultoptions"].update({"fig": False})
        self.shell = Popen([shell], stdin=PIPE, stdout=PIPE, stderr=err_file)
        PwebProcessor.__init__(self, parsed, source, mode, formatdict)
        #self.run_string("__pweave_data__ = {}\n")
        #self.send_data({"rcParams": rcParams, "cwd": self.cwd, "formatdict": self.formatdict})
        self.inline_count = 1  # Count inline code blocks

    def insert_start_tag(self, chunk_id=0, chunk_type="term", id_prefix="results"):
        self.run_string("""printf('<chunk id="%s%i" type="%s">\\n')""" % (id_prefix, chunk_id, chunk_type))

    def insert_close_tag(self):
        self.run_string('printf("</chunk>\\n")')

    def run_string(self, code_string):
        self.shell.stdin.write(("\n" + code_string + "\n").encode('utf-8'))

    def loadstring(self, code_str, chunk=None, scope=None):
        self.insert_start_tag(chunk_type="block", chunk_id=chunk["number"])
        #self.send_data({"chunk": chunk}) #TODO Think of a way to pass options to octave
        self.run_string(code_str)
        self.insert_close_tag()

    def loadterm(self, code_str, chunk=None):
        self.loadstring(code_str, chunk)

    def run_inline_eval(self, code_str):
        self.run_string("disp(%s)" % code_str)

    def run_inline_exec(self, code_str):
        self.run_string(code_str)

    def init_matplotlib(self):
        pass

    def savefigs(self, chunk):
        if chunk['name'] is None:
            prefix = self.basename + '_figure' + str(chunk['number'])
        else:
            prefix = self.basename + '_' + chunk['name']

        figdir = os.path.join(self.cwd, rcParams["figdir"])
        if not os.path.isdir(figdir):
            os.mkdir(figdir)

        fignames = []
        name = rcParams["figdir"] + "/" + prefix + "_" + self.formatdict['figfmt']
        fignames.append(name)
        for fmt in self.formatdict['savedformats']:
            f_name = os.path.join(self.cwd, rcParams["figdir"], prefix + "_" + fmt)
            self.run_string("print -FHelvetica:12 -r200 -d%s %s" % (fmt[1:], f_name))

        return fignames

    def get_figures(self, chunk, result_soup):
        pass


class MatlabProcessor(PwebProcessor):
    """Runs Matlab code usinng python-matlab-brigde"""

    def __init__(self, parsed, source, mode, formatdict):
        from pymatbridge import Matlab
        self.matlab = Matlab()
        self.matlab.start()
        PwebProcessor.__init__(self, parsed, source, mode, formatdict)

    def getresults(self):
        self.matlab.stop()
        return copy.copy(self.executed)

    def loadstring(self, code_string, chunk=None, scope=PwebProcessorGlobals.globals):
        result = self.matlab.run_code(code_string)
        if chunk is not None and len(result["content"]["figures"]) > 0:
            chunk["matlab_figures"] = result["content"]["figures"]
        return result["content"]["stdout"]

    def loadterm(self, code_string, chunk=None):
        result = self.loadstring(code_string)
        return result

    def init_matplotlib(self):
        pass

    def savefigs(self, chunk):
        if not "matlab_figures" in chunk:
            return []


        if chunk['name'] is None:
            prefix = self.basename + '_figure' + str(chunk['number'])
        else:
            prefix = self.basename + '_' + chunk['name']

        figdir = os.path.join(self.cwd, rcParams["figdir"])
        if not os.path.isdir(figdir):
            os.mkdir(figdir)

        fignames = []

        i = 1
        for fig in reversed(chunk["matlab_figures"]): #python-matlab-bridge returns figures in reverse order
            #TODO See if its possible to get diffent figure formats. Either fork python-matlab-bridge or use imagemagick
            name = figdir + "/" + prefix + "_" + str(i) + ".png" #self.formatdict['figfmt']
            shutil.copyfile(fig, name)
            fignames.append(name)
            i += 1

        return fignames

    def add_echo(self, code_str):
        """Format inline chunk code to show results"""
        return "disp(%s)" % code_str

class PwebIPythonProcessor(PwebProcessor):
    """Runs code from parsed Pweave documents"""

    def __init__(self, parsed, source, mode, formatdict):
        PwebProcessor.__init__(self, parsed, source, mode, formatdict)
        import IPython

        x = IPython.core.interactiveshell.InteractiveShell()
        self.IPy = x.get_ipython()
        self.prompt_count = 1

    def loadstring(self, code, **kwargs):
        tmp = StringIO()
        sys.stdout = tmp
        # compiled = compile(code, '<input>', 'exec')
        # exec compiled in PwebProcessorGlobals.globals
        self.IPy.run_cell(code)
        result = "\n" + tmp.getvalue()
        tmp.close()
        sys.stdout = self._stdout
        return result

    def loadterm(self, code_str, **kwargs):
        # Write output to a StringIO object
        # loop trough the code lines
        statement = ""
        prompt = "In [%i]:" % self.prompt_count
        chunkresult = "\n"
        block = code_str.lstrip().splitlines()

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
                chunkresult += ('%s \n' % prompt)

            tmp = StringIO()
            sys.stdout = tmp
            # return_value = eval(compiled_statement, PwebProcessorGlobals.globals)
            self.IPy.run_code(compiled_statement)
            result = tmp.getvalue()
            #if return_value is not None:
            #    result += repr(return_value)
            tmp.close()
            sys.stdout = self._stdout
            if result:
                chunkresult += ("Out[%i]: " % self.prompt_count) + result.rstrip()

            statement = ""
            self.prompt_count += 1
            prompt = 'In [%i]:' % self.prompt_count

        return chunkresult

    def loadinline(self, content):
        """Evaluate code from doc chunks using ERB markup"""
        # Flags don't work with ironpython
        splitted = re.split('(<%[\w\s\W]*?%>)', content)  # , flags = re.S)
        # No inline code
        if len(splitted) < 2:
            return content

        n = len(splitted)

        for i in range(n):
            elem = splitted[i]
            if not elem.startswith('<%'):
                continue
            if elem.startswith('<%='):
                code = elem.replace('<%=', '').replace('%>', '').lstrip()
                result = self.loadstring('print %s,' % code).replace('\n', '', 1)
                splitted[i] = result
                continue
            if elem.startswith('<%'):
                code = elem.replace('<%', '').replace('%>', '').lstrip()
                result = self.loadstring('%s' % code).replace('\n', '', 1)
                splitted[i] = result
        return ''.join(splitted)


class PwebProcessors(object):
    """Lists available input formats"""
    formats = {'python': {'class': PwebProcessor, 'description': 'Python shell'},
               'ipython': {'class': PwebIPythonProcessor, 'description': 'IPython shell'},
               'epython': {'class': PwebSubProcessor, 'description': 'Python as separate process'},
               'octave': {'class': OctaveProcessor, 'description': 'Run code using Octave'},
               'matlab': {'class': MatlabProcessor, 'description': 'Run code using Matlab'}
    }

    @classmethod
    def shortformats(cls):
        fmtstring = ""
        names = list(cls.formats.keys())
        n = len(names)
        for i in range(n):
            fmtstring += " %s" % (names[i])
            if i < (n - 1):
                fmtstring += ","

        return fmtstring

    @classmethod
    def getformats(cls):
        fmtstring = ""
        for format in sorted(cls.formats):
            fmtstring += "* %s:\n   %s\n" % (format, cls.formats[format]['description'])
        return fmtstring

    @classmethod
    def listformats(cls):
        print("\nPweave supported shells:\n")
        print(cls.getformats())
        print("More info: http://mpastell.com/pweave/ \n")



class ProtectStdStreams(object):
    def __init__(self, obj=None):
        self.__obj = obj

    def __enter__(self):
        self.__stdout = sys.stdout
        self.__stderr = sys.stderr
        self.__stdin = sys.stdin
        self.__displayhook = sys.displayhook
        return self.__obj

    def __exit__(self, type, value, traceback):
        sys.stdout = self.__stdout
        sys.stderr = self.__stderr
        sys.stdin = self.__stdin
        sys.displayhook = self.__displayhook
