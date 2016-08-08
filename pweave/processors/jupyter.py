# -*- coding: utf-8 -*-

from jupyter_client.manager import start_new_kernel
from nbformat.v4 import output_from_msg
import os

from ..config import *
from .base import PwebProcessorBase

class JupyterProcessor(PwebProcessorBase):
    
    def __init__(self, parsed, source, mode, formatdict,
                       figdir, outdir, kernel = "python"):
        super(JupyterProcessor, self).__init__(parsed, source, mode, formatdict,
                       figdir, outdir)

        self.extra_arguments = None
        self.timeout = -1
        path = self.outdir
        
        kernel_name = kernel
        #if self.kernel_name:
        #    kernel_name = self.kernel_name
        #self.log.info("Executing notebook with kernel: %s" % kernel_name)
        self.km, self.kc = start_new_kernel(
            kernel_name=kernel_name,
            extra_arguments=self.extra_arguments,
            stderr=open(os.devnull, 'w'),
            cwd=path)
        self.kc.allow_stdin = False
        #self.run_cell("%matplotlib inline\nfrom IPython.display import set_matplotlib_formats\nset_matplotlib_formats('svg', 'pdf')")
		
        
    def close(self):
        self.kc.stop_channels()
        self.km.shutdown_kernel(now = True)
        
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
        return self.run_cell(code_str)
        
    def loadterm(self, code_str, **kwargs):
        return self.run_cell(code_str)