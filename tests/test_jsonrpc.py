import pytest
from geonotebook import jsonrpc

def test_JSONRPCError():
    err = jsonrpc.JSONRPCError('test error')
    assert err.message == 'test error'
    assert err.code == 0
    assert err.data is None
    assert err.toJson() == {'name': 'JSONRPCError',
                            'code': 0,
                            'message': 'JSONRPCError: test error',
                            'data': None}

def test_ParseError():
    assert jsonrpc.ParseError().toJson() == {'name': 'ParseError',
                                             'code': -32700,
                                             'message': 'ParseError: Parse Error.',
                                             'data': None}

def test_InvalidRequest():
    assert jsonrpc.InvalidRequest().toJson() == {'name': 'InvalidRequest',
                                             'code': -32600,
                                             'message': 'InvalidRequest: Invalid Request.',
                                             'data': None}

def test_MethodNotFound():
    assert jsonrpc.MethodNotFound().toJson() == {'name': 'MethodNotFound',
                                             'code':-32601,
                                             'message': 'MethodNotFound: Method not found.',
                                             'data': None}
def test_InvalidParams():
    assert jsonrpc.InvalidParams().toJson() == {'name': 'InvalidParams',
                                             'code': -32602,
                                             'message': 'InvalidParams: Invalid params.',
                                             'data': None}
def test_InternalError():
    assert jsonrpc.InternalError().toJson() == {'name': 'InternalError',
                                             'code': -32603,
                                             'message': 'InternalError: Internal Error.',
                                             'data': None}
def test_ServerError():
    assert jsonrpc.ServerError().toJson() == {'name': 'ServerError',
                                             'code': -32000,
                                             'message': 'ServerError: Server Error.',
                                             'data': None}

def test_is_response_with_result():
    assert jsonrpc.is_response(jsonrpc.json_rpc_result({'some': 'result'}, None, 'MSGID'))

def test_is_response_with_request():
    assert not jsonrpc.is_response(jsonrpc.json_rpc_request('some_method'))

def test_is_response_with_notify():
    assert not jsonrpc.is_response(jsonrpc.json_rpc_notify('some_method'))


def test_is_request_with_result():
    assert not jsonrpc.is_request(jsonrpc.json_rpc_result({'some': 'result'}, None, 'MSGID'))

def test_is_request_with_notify():
    assert not jsonrpc.is_request(jsonrpc.json_rpc_notify('some_method'))

def test_is_request_with_request():
    assert jsonrpc.is_request(jsonrpc.json_rpc_request('some_method'))
