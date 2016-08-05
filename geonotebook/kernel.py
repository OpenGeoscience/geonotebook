from ipykernel.ipkernel import IPythonKernel
import logging
from logging.handlers import SysLogHandler

from inspect import getmembers, ismethod, getargspec
from types import MethodType

import jsonrpc
from jsonrpc import (json_rpc_request,
                     json_rpc_notify,
                     json_rpc_result,
                     is_response,
                     is_request,
                     handle_rpc_response)

from collections import namedtuple

BBox = namedtuple('BBox', ['ulx', 'uly', 'lrx', 'lry'])


class ReplyCallback(object):
    """Stores a message and result/error callbacks for a JSONRPC message.

    This class stores a JSONRPC message and callback which is evaluated
    once the Remote object recieves a 'resolve' call with the message's id.
    This is initialized with a JSONRPC message and a function that takes a
    message and sends it across some transport mechanism (e.g. Websocket).
    """

    def __init__(self, msg, send_message):
        """Initialize the object.

        Creation of the object does not actually send the message. This only
        happens once the the 'then' function is called and reply/error
        callbacks have been set on the object.

        :param msg: a JSONRPC compliant message
        :param send_message: a function that acts as a transport mechanism
        :returns: Nothing
        :rtype: None

        """
        self.state = "CREATED"
        self.msg = msg
        self.send_message = send_message

    def then(self, reply_handler, error_handler):
        """Set reply/error callbacks and send the message.

        :param reply_handler: function that takes the 'result' field
                              of a JSONRPC response object.
        :param error_handler: function that takes the 'error' field
                              of a JSONRPC response object. Should be a
                              well formed JSONRPC error object.
        :returns: self
        :rtype: ReplyCallback

        """
        self.reply_handler = reply_handler
        self.error_handler = error_handler

        self.send_message(self.msg)
        self.state = "PENDING"

        return self

class Remote(object):
    """Provides an object that proxies procedures on a remote object.

    This takes a list of protocol definitions and dynamically generates methods on
    the object that reflect that protocol.  These methods wrap ReplyCallbacks
    objects which manage the reply and error callbacks of a remote proceedure call.
    Remote defines a '_callbacks' variable which is a dict of message id's to
    ReplyCallback objects.
    """


    def validate(self, protocol, *args, **kwargs):
        """Validate a protocol definition.

        :param protocol: Dict containing a single function's protocol
        :returns: Nothing
        :rtype: None

        """
        assert len(args) >= len(protocol["required"]), \
            "Protocol {} has an arity of {}. Called with {}".format(
                protocol['procedure'], len(protocol["required"]), len(args))

        assert len(args) <= len(protocol["required"]) + len(protocol["optional"]), \
            "Protocol {} has an arity of {}. Called with {}".format(
                protocol['procedure'], len(protocol["required"]), len(args))

    def _make_protocol_method(self, protocol):
        """Make a method closure based on a protocol definition

        This takes a protocol and generates a closure that has the same arity as
        the protocol. The closure is dynamically set as a method on the Remote object
        with the same name as protocol. This makes it possible to do:

        Geonotebook._remote.set_center(-74.25, 40.0, 4)

        which will validate the arguments, create a JSONRPC request object, generate a
        ReplyCallback object and store the callback in the _callbacks dict. The message
        is not actually sent until the 'then' function is called on the ReplyCallback
        object ensuring no messages are sent without well defined reply/error callbacks.
        e.g:

        def handle_error(error):
            print "JSONError (%s): %s" % (error['code'], error['message'])

        def handle_reply(result):
            print result

        Geonotebook._remote.set_center(-74.25, 40.0, 4).then(
            handle_reply, handle_error)



        :param protocol: a protocol dict
        :returns: a closure that validates RPC arguments and returns a ReplyCallback
        :rtype: MethodType

        """

        def _protocol_closure(self, *args, **kwargs):
            try:
                self.validate(protocol, *args, **kwargs)
            except Exception as e:
                # TODO: log something here
                raise e

            # Get the paramaters
            params = list(args)
            # Not technically available until ES6
            params.extend([kwargs[k] for k in protocol['optional'] if k in kwargs])

            # Create the message
            msg = json_rpc_request(protocol['procedure'], params)

            # Set up the callback
            self._callbacks[msg['id']] = ReplyCallback(msg, self._send_msg)

            # return the callback
            return self._callbacks[msg['id']]

        return MethodType(_protocol_closure, self, self.__class__)


    def resolve(self, msg):
        """Resolve an open JSONRPC request

        Takes a JSONRPC result message and passes it to either the reply_handler
        or the error_handler of the ReplyCallback object.

        :param msg: JSONRPC result message
        :returns: Nothing
        :rtype: None

        """
        if msg['id'] in self._callbacks:
            try:
                if msg['error'] is not None:
                    self._callbacks[msg['id']].error_handler(msg['error'])
                else:
                    self._callbacks[msg['id']].reply_handler(msg['result'])

            except Exception as e:
                raise e
            finally:
                del self._callbacks[msg['id']]
        else:
            self.log.warn("Could not find callback with id %s" % msg['id'])


    def __init__(self, transport, protocol):
        """Initialize the Remote object.

        :param transport: function that takes a JSONRPC request message
        :param protocol: A list of protocol definitions for remote functions
        :returns: Nothing
        :rtype: None

        """

        self._callbacks = {}
        self._send_msg = transport
        self.protocol = protocol

        for p in self.protocol:
            assert 'procedure' in p, \
                ""
            assert 'required' in p, \
                ""
            assert 'optional' in p, \
                ""

            setattr(self, p['procedure'], self._make_protocol_method(p))




class Geonotebook(object):
    msg_types = ['get_protocol', 'set_center', 'set_region']

    _protocol = None
    _remote = None

    @classmethod
    def class_protocol(cls):
        """Initializes the RPC protocol description.

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
        # If this is a response,  pass it along to the Remote object to be
        # processesd by the correct reply/error handler
        if is_response(msg):
            self._remote.resolve(msg)

        # Otherwise process the request from the remote RPC client.
        elif is_request(msg):
            method, params = msg['method'], msg['params']

            if method in self.msg_types:
                try:
                    result = getattr(self, method)(*params)
                    self._send_msg(json_rpc_result(result, None, msg['id']))
                except Exception as e:
                    if isinstance(e, jsonrpc.JSONRPCError):
                        raise e
                    else:
                        raise jsonrpc.ServerError(str(e))
            else:
                raise jsonrpc.MethodNotFound("Method not allowed")
        else:
            raise jsonrpc.ParseError("Could not parse msg: %s" % msg)

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
        self.log.error("JSONRPCError (%s): %s" % (error['code'], error['message']))

    ### RPC endpoints ###

    def set_center(self, x, y, z):

        def _set_center(result):
            self.x, self.y, self.z  = result

        cb = self._remote.set_center(x, y, z).then(_set_center, self.rpc_error)
        return cb


    def set_region(self, ulx, uly, lrx, lry):
        if ulx == lrx and uly == lry:
            raise jsonrpc.InvalidParams("Bounding box values cannot be the same!")


        self.region = BBox(ulx, uly, lrx, lry)
        return ulx, uly, lrx, lry

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

    def handle_comm_msg(self, message):
        """Handler for incomming comm messages

        :param msg: a Comm message
        :returns: Nothing
        :rtype: None

        """
        msg = self._unwrap(message)

        try:
            self.geonotebook._recv_msg(msg)

        except jsonrpc.JSONRPCError as e:
            self.geonotebook._send_msg(json_rpc_result(None, e.toJson(), msg['id']))
            self.log.error(u"JSONRPCError (%s): %s" % (e.code, e.message))

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

        # TODO: Check if the msg is empty - no protocol - die
        self.geonotebook._remote = Remote(self.comm.send, self._unwrap(msg))
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
