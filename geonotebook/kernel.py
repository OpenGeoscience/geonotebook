from ipykernel.ipkernel import IPythonKernel
import logging
from logging.handlers import SysLogHandler

from inspect import getmembers, ismethod, getargspec
from types import MethodType

from jsonrpc import (json_rpc_request,
                     json_rpc_notify,
                     is_response,
                     is_request,
                     handle_rpc_response)

from collections import namedtuple

BBox = namedtuple('BBox', ['ulx', 'uly', 'lrx', 'lry'])

class Geonotebook(object):
    msg_types = ['get_protocol', 'set_center', 'set_region']

    _protocol = None
    _remote = None

    class Remote(object):
        """Provides an object that proxies procedures on a remote object.

        This takes a protocol definition and dynamically generates methods on
        the object that reflect that protocol.  Once instantiated it allows for
        sending one-way messages to the remote client via the kernel's comm object.
        This object is intended to be used internally because it does not manage
        the request/reply cycle nessisary to ensure we have consistent
        client/server state.
        """
        def validate(self, protocol, *args, **kwargs):
            assert len(args) >= len(protocol["required"]), \
                "Protocol {} has an arity of {}. Called with {}".format(
                    protocol['procedure'], len(protocol["required"]), len(args))

            assert len(args) <= len(protocol["required"]) + len(protocol["optional"]), \
                "Protocol {} has an arity of {}. Called with {}".format(
                    protocol['procedure'], len(protocol["required"]), len(args))

        def _make_protocol_method(self, protocol):
            """Make a method closure based on a protocol definition

            This takes a protocol and generates a closure that accepts
            functions to execute the remote procedure call.  This closure
            is set on the Notebook _remote object making it possible to do:

            Geonotebook._remote.set_center(-74.25, 40.0, 4)

            which will validate the argumetns and send the message of the
            comm.

            :param protocol: a protocol dict
            :returns: a closure that validates and executes the RPC
            :rtype: MethodType

            """

            def _protocol_closure(self, *args, **kwargs):
                try:
                    self.validate(protocol, *args, **kwargs)
                except Exception as e:
                    # log something here
                    raise e

                params = list(args)
                # Not technically available until ES6
                params.extend([kwargs[k] for k in protocol['optional'] if k in kwargs])

                return self._send_msg(
                    json_rpc_request(protocol['procedure'], params))

            return MethodType(_protocol_closure, self, self.__class__)

        def _send_msg(self, msg):
            self.notebook._send_msg(msg)
            return msg

        def __init__(self, notebook, protocol):
            self.notebook = notebook
            self.protocol = protocol

            for p in self.protocol:
                assert 'procedure' in p, \
                    ""
                assert 'required' in p, \
                    ""
                assert 'optional' in p, \
                    ""

                setattr(self, p['procedure'], self._make_protocol_method(p))


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
                return {'procedure': fn,
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
        if is_response(msg):
            if msg['id'] in self._callbacks:
                # TODO Needs to be more sophisticated - add errbacks etc
                # Some kind of deferred implementation

                self._callbacks[msg['id']](msg)
                del self._callbacks[msg['id']]
            else:
                self.log.warn("Could not find callback with id %s" % msg['id'])

        elif is_request(msg):
            method, params = msg['method'], msg['params']
            if method in self.msg_types:
                getattr(self, method)(*params)
        else:
            raise Exception("Could not parse msg: %s" % msg)

    @property
    def log(self):
        return self._kernel.log

    def __init__(self, kernel, *args, **kwargs):

        self._protocol = None
        self.view_port = None
        self.region = None
        self.x = None
        self.y = None
        self.z = None

        self._kernel = kernel

        self._callbacks = {}

    def rpc_error(self, error):
        self.log.error("(%s): %s" % (error['code'], error['message']))

    ### RPC endpoints ###

    def set_center(self, x, y, z):

        @handle_rpc_response(self.rpc_error)
        def _callback(msg):
            self.x = x
            self.y = y
            self.z = z


        msg = self._remote.set_center(x, y, z)
        self._callbacks[msg['id']] = _callback
        # TODO:  Need some way to visually make it appear that the cell is
        #        working, for request/reply messages. We don't want to actually
        #        tie up the kernel,  but we do need to be able to return
        #        results and errors to the cell output area as though it were a
        #        syncrhonous operation.
        return None

    def set_region(self, ulx, uly, lrx, lry):
        self.region = BBox(ulx, uly, lrx, lry)

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

        self.comm = comm
        self.comm.on_msg(self.handle_comm_msg)

        # Check if the msg is empty - no protocol - die
        self.geonotebook._remote = Geonotebook.Remote(self.geonotebook, self._unwrap(msg))
        # Reply to the open comm,  this should probably be set up on
        # self.geonotebook._remote as an actual proceedure call
        self.comm.send({
            "method": "set_protocol",
            "data": self.geonotebook.get_protocol()
        })


    def __init__(self, **kwargs):
        kwargs['log'].setLevel(logging.INFO)
        self.log = kwargs['log']

        self.geonotebook = Geonotebook(self)
        super(GeonotebookKernel, self).__init__(**kwargs)


        self.shell.user_ns.update({'M': self.geonotebook})

        self.comm_manager.register_target('geonotebook', self.handle_comm_open)
