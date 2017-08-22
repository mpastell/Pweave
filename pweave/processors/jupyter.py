# -*- coding: utf-8 -*-

from jupyter_client.manager import start_new_kernel
from jupyter_client import KernelManager
from nbformat.v4 import output_from_msg
import os

from .. import config
from .base import PwebProcessorBase
from . import subsnippets
from IPython.core import inputsplitter
from ipykernel.inprocess import InProcessKernelManager

from queue import Empty


class JupyterProcessor(PwebProcessorBase):
    """Generic Jupyter processor, should work with any kernel"""

    def __init__(self, parsed, kernel, source, mode,
                       figdir, outdir, embed_kernel=False):
        super(JupyterProcessor, self).__init__(parsed, kernel, source, mode,
                       figdir, outdir)

        self.extra_arguments = None
        self.timeout = -1
        path = os.path.abspath(outdir)

        if embed_kernel:
            km = InProcessKernelManager(kernel_name=kernel)
        else:
            km = KernelManager(kernel_name=kernel)

        km.start_kernel(cwd=path, stderr=open(os.devnull, 'w'), history=False)
        kc = km.client()
        kc.start_channels()
        try:
            kc.wait_for_ready()
        except RuntimeError:
            print("Timeout from starting kernel\nTry restarting python session and running weave again")
            kc.stop_channels()
            km.shutdown_kernel()
            raise

        self.km = km
        self.kc = kc
        self.kc.allow_stdin = False


    def close(self):
        self.kc.stop_channels()
        self.km.shutdown_kernel()


    def run_cell(self, src):
        cell = {}
        cell["source"] = src.lstrip()
        msg_id = self.kc.execute(src.lstrip())

        # wait for finish, with timeout
        while True:
            try:
                timeout = self.timeout
                if timeout < 0:
                    timeout = None
                msg = self.kc.get_shell_msg(timeout=timeout)
            except Empty:
                if self.interrupt_on_timeout:
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
                msg = self.kc.iopub_channel.get_msg(block=True, timeout=4)
            except Empty:
                print("Timeout waiting for IOPub output\nTry restarting python session and running weave again")
                raise RuntimeError("Timeout waiting for IOPub output")

            #stdout from InProcessKernelManager has no parent_header
            if msg['parent_header'].get('msg_id') != msg_id and msg['msg_type'] != "stream":
                continue

            msg_type = msg['msg_type']
            content = msg['content']

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
                print("unhandled iopub msg: " + msg_type)
            else:
                outs.append(out)

        return outs

    def loadstring(self, code_str, **kwargs):
        return self.run_cell(code_str)

    #Yes same format for compatibility even if term is not implemented
    def loadterm(self, code_str, **kwargs):
        return((sources, self.run_cell(code_str)))

    #TODO add support for "rich" output
    #Requires storing the results for formatter
    def load_inline_string(self, code_string):
        from nbconvert import filters
        outputs = self.loadstring(code_string)
        result = ""
        for out in outputs:
            if out["output_type"] == "stream":
                result += out["text"]
            elif out["output_type"] == "error":
                result += filters.strip_ansi("".join(out["traceback"]))
            elif "text/plain" in out["data"]:
                result += out["data"]["text/plain"]
            else:
                result = ""
        return result


class IPythonProcessor(JupyterProcessor):
    """Contains IPython specific functions"""

    def __init__(self, *args):
        kernel = args[1]

        if kernel == "python3":
            embed = True
        else:
            embed = False

        super(IPythonProcessor, self).__init__(*args, embed_kernel=embed)
        if config.rcParams["usematplotlib"]:
            self.init_matplotlib()

    def init_matplotlib(self):
        self.loadstring(subsnippets.init_matplotlib)

    def pre_run_hook(self, chunk):
        f_size = """matplotlib.rcParams.update({"figure.figsize" : (%i, %i)})""" % chunk["f_size"]
        f_dpi = """matplotlib.rcParams.update({"savefig.dpi" : %i})""" % chunk["dpi"]
        self.loadstring("\n".join([f_size, f_dpi]))

    def loadterm(self, code_str, **kwargs):
        splitter = inputsplitter.IPythonInputSplitter()
        code_lines = code_str.lstrip().splitlines()
        sources = []
        outputs = []

        for line in code_lines:
            if splitter.push_accepts_more():
                splitter.push_line(line)
            else:
                code_str = splitter.source
                sources.append(code_str)
                out = self.loadstring(code_str)
                #print(out)
                outputs.append(out)
                splitter.reset()
                splitter.push_line(line)


        if splitter.source != "":
            code_str = splitter.source
            sources.append(code_str)
            out = self.loadstring(code_str)
            outputs.append(out)

        return((sources, outputs))
