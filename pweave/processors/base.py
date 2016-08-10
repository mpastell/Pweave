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
from ..config import *


class PwebProcessorBase(object):
    """Processors run code from parsed Pweave documents. This is an abstract base
    class for specific implementations"""

    def __init__(self, parsed, kernel, source, mode,
                       figdir, outdir):
        self.parsed = parsed
        self.source = source
        self.documentationmode = mode
        self.figdir = figdir
        self.outdir = outdir

        self.cwd = os.path.dirname(os.path.abspath(source))
        self.basename = os.path.basename(os.path.abspath(source)).split(".")[0]
        self.pending_code = ""  # Used for multichunk splits

    def run(self):
        # Create directory for figures
        self.ensureDirectoryExists(self.getFigDirectory())
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
        self.close()

    def close(self):
        pass

    def ensureDirectoryExists(self, figdir):
        if not os.path.isdir(figdir):
            os.mkdir(figdir)

    def getresults(self):
        return copy.deepcopy(self.executed)

    def store(self, data):
        """A method used to pickle stuff for persistence"""
        cachedir = os.path.join(self.cwd, rcParams["cachedir"])
        self.ensureDirectoryExists(cachedir)

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
            # This is a bit redundant,
            # it is added afterwards to support adding options as
            # metadata to notebooks
            chunk["options"] = defaults
            #del chunk['options']

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

            self.pre_run_hook(chunk)

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

        self.post_run_hook(chunk)


        return chunk

    def post_run_hook(self, chunk):
        pass

    def pre_run_hook(self, chunk):
        pass

    def init_matplotlib(self):
        pass

    def savefigs(self, chunk):
        pass
      
    def getFigDirectory(self):
        return os.path.join(self.outdir, self.figdir)

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
        pass
      
    def loadstring(self, code, chunk=None, scope=PwebProcessorGlobals.globals):
        pass

    def loadterm(self, code_string, chunk=None):
        pass

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
