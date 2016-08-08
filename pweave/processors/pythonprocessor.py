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

from .base import PwebProcessorBase, ProtectStdStreams


class PwebProcessor(PwebProcessorBase):
    """Run code from chunks using exec and eval in same process. This processor
    has its own scope
    """

    def __init__(self, parsed, source, mode, formatdict,
                       figdir, outdir):
        super(PwebProcessor, self).__init__(parsed, source, mode, formatdict,
                       figdir, outdir)
        self._stdout = sys.stdout

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

        self.ensureDirectoryExists(self.getFigDirectory())

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

                name = self.figdir + "/" + prefix + "_" + str(i) + \
                       self.formatdict['figfmt']

                for format in self.formatdict['savedformats']:
                    f_name = os.path.join(self.getFigDirectory(),
                                          prefix + "_" + str(i)) + format
                    plt.savefig(f_name)

                    plt.draw()
                fignames.append(name)
                plt.close()

        return fignames

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
                        content = cmd.communicate(timeout=20)[0].decode('utf-8').replace("\r", "") + "\n"
                    except TimeoutExpired:
                        cmd.kill()
                        content, errs = cmd.communicate()
                        sys.stdout.write("Shell command timeout:\n %s\n" % line)
                        content = content.decode('utf-8').replace("\r", "") + "\n"
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


class ConsoleEmulator(object):
    """Emulate console for running code chunks with term=True"""

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
