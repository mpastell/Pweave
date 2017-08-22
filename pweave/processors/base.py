# Processors that execute code from code chunks
import sys
import re
import os
import io
import copy
from ..config import *
import pickle

class PwebProcessorBase(object):
    """Processors run code from parsed Pweave documents. This is an abstract base
    class for specific implementations"""

    def __init__(self, parsed, kernel, source, docmode,
                       figdir, outdir):
        self.parsed = parsed
        self.source = source
        self.documentationmode = docmode
        self.figdir = figdir
        self.outdir = outdir
        self.executed = []

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

        self.executed = []

        # Term chunk returns a list of dicts, this flattens the results
        for chunk in self.parsed:
            res = self._runcode(chunk)
            if isinstance(res, list):
                self.executed = self.executed + res
            else:
                self.executed.append(res)


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
        #flattened = list(itertools.chain.from_iterable(self.executed))
        return copy.deepcopy(self.executed)

    def store(self, data):
        """Cache the results"""
        cachedir = os.path.join(self.cwd, rcParams["cachedir"])
        self.ensureDirectoryExists(cachedir)

        name = cachedir + "/" + self.basename + ".pkl"
        f = open(name, 'wb')
        pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)
        f.close()

    def restore(self):
        """Restore results from cache"""
        cachedir = os.path.join(self.cwd, rcParams["cachedir"])
        name = cachedir + "/" + self.basename + ".pkl"

        if os.path.exists(name):
            f = open(name, 'rb')
            self._oldresults = pickle.load(f)
            f.close()
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
                # Running in term mode can return a list of chunks
                chunks = []
                sources, results = self.loadterm(chunk['content'], chunk=chunk)
                n = len(sources)
                content = ""
                for i in range(n):
                    if len(results[i]) == 0:
                        content += sources[i]
                    else:
                        new_chunk = chunk.copy()
                        new_chunk["content"] = content + sources[i].rstrip()
                        content = ""
                        new_chunk["result"] = results[i]
                        chunks.append(new_chunk)

                #Deal with not output, #73 
                if len(content) > 0:
                    new_chunk = chunk.copy()
                    new_chunk["content"] = content
                    new_chunk["result"] = ""
                    chunks.append(new_chunk)

                return(chunks)
            else:
                chunk['result'] = self.loadstring(chunk['content'], chunk=chunk)

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
                chunks = [c for c in self._oldresults if c["number"] == i and c["type"] == "code"]
                executed = executed + chunks

        self.executed = executed
        return True

    def load_shell(self, chunk):
        pass

    def loadstring(self, code, chunk=None):
        pass

    def loadterm(self, code_string, chunk=None):
        pass

    def load_inline_string(self, code_string):
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
                result = self.load_inline_string(code_str).strip()
                splitted[i] = result
                continue
            if elem.startswith('<%'):
                code_str = elem.replace('<%', '').replace('%>', '').lstrip()
                result = self.load_inline_string(code_str).strip()
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
