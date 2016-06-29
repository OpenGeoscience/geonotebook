from ipykernel.ipkernel import IPythonKernel
import logging
from logging.handlers import SysLogHandler
# ns = require('base/js/namespace')
# var cm = ns.notebook.kernel.comm_manager

class Geonotebook(object):
    def __init__(self, kernel, *args, **kwargs):
        self._kernel = kernel

    def _send_msg(self, msg):
        self._kernel.comm.send(msg)


class GeonotebookKernel(IPythonKernel):
    def handle_comm_msg(self, msg):
        self.log.info(msg['content']['data'])
        if msg['content']['data'] == 'PING':
            self.comm.send("ACK")

    def handle_comm_open(self, comm, msg):
        self.comm = comm
        self.comm.on_msg(self.handle_comm_msg)


    def __init__(self, **kwargs):
        kwargs['log'].setLevel(logging.DEBUG)

        self.geonotebook = Geonotebook(self)
        super(GeonotebookKernel, self).__init__(**kwargs)


        self.shell.user_ns.update({'map': self.geonotebook})

        self.comm_manager.register_target('test', self.handle_comm_open)
