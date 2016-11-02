import uuid
from promise import Promise
from types import MethodType


class JSONRPCError(Exception):
    code = 0
    message = None
    data = None
    status = 500

    def __init__(self, message=None):
        if message is not None:
            self.message = message

    def toJson(self):
        return {
            'name': self.__class__.__name__,
            'code': self.code,
            'message': "%s: %s" % (self.__class__.__name__, self.message),
            'data': self.data
        }


class ParseError(JSONRPCError):
    code = -32700
    message = "Parse Error."


class InvalidRequest(JSONRPCError):
    code = -32600
    message = "Invalid Request."


class MethodNotFound(JSONRPCError):
    code = -32601
    message = "Method not found."


class InvalidParams(JSONRPCError):
    code = -32602
    message = "Invalid params."


class InternalError(JSONRPCError):
    code = -32603
    message = "Internal Error."


class ServerError(JSONRPCError):
    code = -32000
    message = "Server Error."


def is_response(msg):
    return 'result' in msg and 'error' in msg and 'id' in msg


def is_request(msg):
    return 'method' in msg and 'params' in msg and 'id' in msg


def json_rpc_result(result, error, msg_id):
    return {
        "result": result,
        "error": error,
        "id": msg_id}


def json_rpc_request(method, params=None, jsonrpc="2.0"):
    return {
        "method": method,
        "params": params,
        "jsonrpc": jsonrpc,
        "id": str(uuid.uuid4())}


def json_rpc_notify(method, params=None, jsonrpc="2.0"):
    return {
        "method": method,
        "params": params,
        "jsonrpc": jsonrpc}


class Remote(object):
    """Provides an object that proxies procedures on a remote object.

    This takes a list of protocol definitions and dynamically generates
    methods on the object that reflect that protocol.  These methods wrap
    Promises which manage the reply and error callbacks of a remote proceedure
    call. Remote defines a '_promises' variable which is a dict of message
    id's to Promises.
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
        Promise and store it in the _promises dict.
        e.g:

        def handle_error(error):
            print "JSONError (%s): %s" % (error['code'], error['message'])

        def handle_reply(result):
            print(result)

        Geonotebook._remote.set_center(-74.25, 40.0, 4).then(
            handle_reply, handle_error)



        :param protocol: a protocol dict
        :returns: a closure that validates RPC arguments and returns a Promise
        :rtype: MethodType

        """

        assert 'required' in protocol, \
            "protocol {} must define required arguments".format(
                protocol['procedure'])
        assert 'optional' in protocol, \
            "protocol {} must define optional arguments".format(
                protocol['procedure'])

        for arg in protocol["required"]:
            assert 'key' in arg, \
                "protocol {} is malfomred, argument {} does not have a key".format(
                    protocol['procedure'], arg)

        for arg in protocol["optional"]:
            assert 'key' in arg, \
                "protocol {} is malfomred, argument {} does not have a key".format(
                    protocol['procedure'], arg)


        def _protocol_closure(self, *args, **kwargs):
            try:
                self.validate(protocol, *args, **kwargs)
            except Exception as e:
                # TODO: log something here
                raise e

            def make_param(key, value, required=True):
                return {'key': key, 'value': value, 'required': required}
            # Get the paramaters
            params = [make_param(k['key'], v) for k,v in zip(protocol['required'], args)]
            # Not technically available until ES6
            params.extend([make_param(k['key'], kwargs[k['key']], required=False)
                           for k in protocol['optional'] if k['key'] in kwargs])

            # Create the message
            msg = json_rpc_request(protocol['procedure'], params)

            # Set up the callback
            self._promises[msg['id']] = Promise()
            self._send_msg(msg)

            # return the callback
            return self._promises[msg['id']]

        return MethodType(_protocol_closure, self)

    def resolve(self, msg):
        """Resolve an open JSONRPC request

        Takes a JSONRPC result message and passes it to either the on_fulfilled handler
        or the on_rejected handler of the Promise.

        :param msg: JSONRPC result message
        :returns: Nothing
        :rtype: None

        """
        if msg['id'] in self._promises:
            try:
                if msg['error'] is not None:
                    self._promises[msg['id']].reject(Exception(msg['error']))
                else:
                    self._promises[msg['id']].fulfill(msg['result'])

            except Exception as e:
                raise e
        else:
            self.log.warn("Could not find promise with id %s" % msg['id'])


    def __init__(self):
        """Initialize the Remote object.

        :param transport: function that takes a JSONRPC request message
        :param protocol: A list of protocol definitions for remote functions
        :returns: Nothing
        :rtype: None

        """

        self._promises = {}

    def __call__(self, transport, protocol):
        self._send_msg = transport
        self.protocol = protocol

        for p in self.protocol:
            assert 'procedure' in p, \
                ""

            setattr(self, p['procedure'], self._make_protocol_method(p))

        return self

remote = Remote()
