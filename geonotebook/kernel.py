from ipykernel.ipkernel import IPythonKernel
import logging
from logging.handlers import SysLogHandler

from inspect import getmembers, ismethod, getargspec

class Geonotebook(object):
    msg_types = ['get_protocol', 'set_center', 'set_region']

    _protocol = None

    def __init__(self, kernel, *args, **kwargs):
        self._protocol = None
        self.view_port = None
        self.region = None
        self._kernel = kernel

    @classmethod
    def class_protocol(cls):
        """Initializes the RPC protocol description

        Provides a static, lazy loaded description of the functions that
        are available to be called by the RPC mechanism.

        :param cls: The class (e.g. Geonotebook)
        :returns: the protocol description
        :rtype: dict

        """

        if cls._protocol is None:
            def _method_protocol(fn, method):
                spec = getargspec(method)

                # spec.args[1:] so we don't include 'self'
                params = spec.args[1:]
                # The number of optional arguments
                d = len(spec.defaults) if spec.defaults is not None else 0
                # The number of required arguments
                r = len(params) - d

                # Would be nice to include whether or to expect a reply, or
                # If this is just a notification function
                return {'proceedure': fn,
                        'required': params[:r],
                        'optional': params[r:]}

            cls._protocol = [_method_protocol(fn, method) for fn, method in
                             getmembers(cls, predicate=ismethod) if fn in cls.msg_types]
        return cls._protocol


    def _send_msg(self, msg):
        """Send a message to the client.

        'msg' should be a well formed RPC message.

        :param msg: The RPC message
        :returns: Nothing
        :rtype: None

        """

        self._kernel.comm.send(msg)

    def _recv_msg(self, msg):
        """Recieve an RPC message from the client

        :param msg: An RPC message
        :returns: Nothing
        :rtype: None

        """

        assert 'msg_type' in msg, \
            u"'msg_type' must be defined!"
        assert msg['msg_type'] in self.msg_types, \
            u"'msg_type' must be one of {}".format(",".join(self.msg_types))

    ### RPC endpoints ###

    def set_center(self, x, y, z):
        pass

    def set_region(self, bounding_box=None):
        pass

    def get_protocol(self):
        return self.__class__.class_protocol()





class GeonotebookKernel(IPythonKernel):
    def _unwrap(self, msg):
        """Unwrap a Comm message

        Remove the Comm envolpe and return an RPC message

        :param msg: the Comm message
        :returns: An RPC message
        :rtype: dict

        """

        return msg['content']['data']

    def handle_comm_msg(self, msg):
        """Handler for incomming comm messages

        :param msg: a Comm message
        :returns: Nothing
        :rtype: None

        """

        try:
            self.geonotebook._recv_msg(self._unwrap(msg))
        except Exception as e:
            self.log.error(u"Error processing msg: {}".format(str(e)))


    def handle_comm_open(self, comm, msg):
        """Handler for opening a comm

        :param comm: The comm to open
        :param msg: The initial comm_open message
        :returns: Nothing
        :rtype: None

        """

        # TODO: msg should contain a protocol definition for the client side
        #       handle comm msg can return a closure that includes the client
        #       side protocol - protocol should be converted to an proxy class
        #       so we can call functions (as promises?)
        self.comm = comm
        self.comm.on_msg(self.handle_comm_msg)


    def __init__(self, **kwargs):
        kwargs['log'].setLevel(logging.DEBUG)

        self.geonotebook = Geonotebook(self)
        super(GeonotebookKernel, self).__init__(**kwargs)


        self.shell.user_ns.update({'M': self.geonotebook})

        self.comm_manager.register_target('geonotebook', self.handle_comm_open)
