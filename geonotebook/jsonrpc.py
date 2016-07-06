import json

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


def json_rpc_request(method, params=None, jsonrpc="2.0"):
    return {
        "method": method,
        "params": params,
        "jsonrpc": jsonrpc,
        "id": "TESTID"}

def json_rpc_notify(method, params=None, jsonrpc="2.0"):
    return {
        "method": method,
        "params": params,
        "jsonrpc": jsonrpc}
