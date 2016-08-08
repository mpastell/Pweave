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
from jupyter_client.manager import start_new_kernel
from nbformat.v4 import output_from_msg


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



class PwebSubProcessor(PwebProcessor):
    """Runs code in external Python shell using subprocess.Popen"""

    def __init__(self, parsed, source, mode, formatdict,
                        figdir, outdir):
        err_file = open(os.path.dirname(os.path.abspath(source))
                    + "/epython_stderr.log", "wt")
        shell = rcParams["shell_path"]
        self.shell = Popen([shell, "-i", "-u"], stdin=PIPE, stdout=PIPE, stderr=err_file)
        PwebProcessor.__init__(self, parsed, source,
                mode, formatdict, figdir, outdir)
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

        figdir = self.getFigDirectory()
        self.ensureDirectoryExists(figdir)

        self.send_data({"figdir": figdir, "prefix": prefix})

        from . import subsnippets

        self.run_string(subsnippets.savefigs)

    def init_matplotlib(self):
        if rcParams["usematplotlib"]:
            self.run_string("\nimport matplotlib\nmatplotlib.use('Agg')\nimport matplotlib.pyplot as plt\n")


class OctaveProcessor(PwebSubProcessor):
    def __init__(self, parsed, source, *args, **kwargs):
        super(OctaveProcessor, self).__init__(parsed, source, *args, **kwargs)
        err_file = open(os.path.dirname(os.path.abspath(source)) + "/octave_stderr.log", "wt")
        shell = "octave"
        #shell = rcParams["shell_path"]

        rcParams["chunk"]["defaultoptions"].update({"fig": False})
        self.shell = Popen([shell], stdin=PIPE, stdout=PIPE, stderr=err_file)
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

        self.ensureDirectoryExists(self.getFigDirectory())

        fignames = []
        name = self.figdir + "/" + prefix + "_" + self.formatdict['figfmt']
        fignames.append(name)
        for fmt in self.formatdict['savedformats']:
            f_name = os.path.join(self.getFigDirectory(),
                                  prefix + "_" + fmt)
            self.run_string("print -FHelvetica:12 -r200 -d%s %s" % (fmt[1:], f_name))

        return fignames

    def get_figures(self, chunk, result_soup):
        pass


class MatlabProcessor(PwebProcessor):
    """Runs Matlab code usinng python-matlab-brigde"""

    def __init__(self, *args, **kwargs):
        super(MatlabProcessor, self).__init__(*args, **kwargs)
        from pymatbridge import Matlab
        self.matlab = Matlab()
        self.matlab.start()

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

        figdir = self.getFigDirectory()
        self.ensureDirectoryExists(figdir)

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

    def __init__(self, *args, **kwargs):
        super(PwebIPythonProcessor, self).__init__(*args, **kwargs)

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

class JupyterProcessor(PwebProcessor):
    
    def __init__(self, parsed, source, mode, formatdict,
                       figdir, outdir):
        super(JupyterProcessor, self).__init__(parsed, source, mode, formatdict,
                       figdir, outdir)

        self.extra_arguments = None
        self.timeout = -1
        path = "."
        
        kernel_name = "python"
        #if self.kernel_name:
        #    kernel_name = self.kernel_name
        #self.log.info("Executing notebook with kernel: %s" % kernel_name)
        self.km, self.kc = start_new_kernel(
            kernel_name=kernel_name,
            extra_arguments=self.extra_arguments,
            stderr=open(os.devnull, 'w'),
            cwd=path)
        self.kc.allow_stdin = False

        
    def close(self):
        self.kc.stop_channels()
        self.km.shutdown_kernel(now=self.shutdown_kernel == 'immediate')
        
    def run_cell(self, src):
        cell = {}
        cell["source"] = src
        msg_id = self.kc.execute(src)
        print(msg_id)
        #self.log.debug("Executing cell:\n%s", cell.source)
        
        # wait for finish, with timeout
        while True:
            try:
                timeout = self.timeout
                if timeout < 0:
                    timeout = None
                msg = self.kc.shell_channel.get_msg(timeout=timeout)
            except Empty:
                #self.log.error(
                #    "Timeout waiting for execute reply (%is)." % self.timeout)
                if self.interrupt_on_timeout:
                    #self.log.error("Interrupting kernel")
                    self.km.interrupt_kernel()
                    break
                else:
                    try:
                        exception = TimeoutError
                    except NameError:
                        exception = RuntimeError
                    raise exception(
                        "Cell execution timed out, see log for details.")

            if msg['parent_header'].get('msg_id') == msg_id:
                break
            else:
                # not our reply
                continue

        outs = []

        while True:
            try:
                # We've already waited for execute_reply, so all output
                # should already be waiting. However, on slow networks, like
                # in certain CI systems, waiting < 1 second might miss messages.
                # So long as the kernel sends a status:idle message when it
                # finishes, we won't actually have to wait this long, anyway.
                msg = self.kc.iopub_channel.get_msg(timeout=4)
            except Empty:
                self.log.warn("Timeout waiting for IOPub output")
                if self.raise_on_iopub_timeout:
                    raise RuntimeError("Timeout waiting for IOPub output")
                else:
                    break
            if msg['parent_header'].get('msg_id') != msg_id:
                # not an output from our execution
                continue

            msg_type = msg['msg_type']
            #self.log.debug("output: %s", msg_type)
            content = msg['content']

            #print(msg)
            # set the prompt number for the input and the output
            if 'execution_count' in content:
                cell['execution_count'] = content['execution_count']

            if msg_type == 'status':
                if content['execution_state'] == 'idle':
                    break
                else:
                    continue
            elif msg_type == 'execute_input':
                continue
            elif msg_type == 'clear_output':
                outs = []
                continue
            elif msg_type.startswith('comm'):
                continue

            try:
                out = output_from_msg(msg)
            except ValueError:
                self.log.error("unhandled iopub msg: " + msg_type)
            else:
                outs.append(out)

        return outs

	def loadstring(self, code_str, **kwargs):
		return self.run_cell(code)
        
    def loadterm(self, code_str, **kwargs):
        return self.run_cell(code)
    
      
class PwebProcessors(object):
    """Lists available input formats"""
    formats = {'python': {'class': PwebProcessor,
                          'description': 'Python shell'},
               'ipython': {'class': PwebIPythonProcessor,
                           'description': 'IPython shell'},
               'epython': {'class': PwebSubProcessor,
                           'description': 'Python as separate process'},
               'octave': {'class': OctaveProcessor,
                          'description': 'Run code using Octave'},
               'matlab': {'class': MatlabProcessor,
                          'description': 'Run code using Matlab'},
               'jupyter': {'class': JupyterProcessor,
                          'description': 'Run code using Jupyter client'}}

    @classmethod
    def getProcessor(cls, shell):
        return cls.formats[shell]['class']

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
