from geonotebook import jsonrpc


def test_JSONRPCError():  # noqa: N802
    err = jsonrpc.JSONRPCError('test error')
    assert err.message == 'test error'
    assert err.code == 0
    assert err.data is None
    assert err.tojson() == {
        'name': 'JSONRPCError',
        'code': 0,
        'message': 'JSONRPCError: test error',
        'data': None
    }


def test_ParseError():  # noqa: N802
    assert jsonrpc.ParseError().tojson() == {
        'name': 'ParseError',
        'code': -32700,
        'message': 'ParseError: Parse Error.',
        'data': None
    }


def test_InvalidRequest():  # noqa: N802
    assert jsonrpc.InvalidRequest().tojson() == {
        'name': 'InvalidRequest',
        'code': -32600,
        'message': 'InvalidRequest: Invalid Request.',
        'data': None
    }


def test_MethodNotFound():  # noqa: N802
    assert jsonrpc.MethodNotFound().tojson() == {
        'name': 'MethodNotFound',
        'code': -32601,
        'message': 'MethodNotFound: Method not found.',
        'data': None
    }


def test_InvalidParams():  # noqa: N802
    assert jsonrpc.InvalidParams().tojson() == {
        'name': 'InvalidParams',
        'code': -32602,
        'message': 'InvalidParams: Invalid params.',
        'data': None
    }


def test_InternalError():  # noqa: N802
    assert jsonrpc.InternalError().tojson() == {
        'name': 'InternalError',
        'code': -32603,
        'message': 'InternalError: Internal Error.',
        'data': None
    }


def test_ServerError():  # noqa: N802
    assert jsonrpc.ServerError().tojson() == {
        'name': 'ServerError',
        'code': -32000,
        'message': 'ServerError: Server Error.',
        'data': None
    }


def test_is_response_with_result():
    assert jsonrpc.is_response(
        jsonrpc.json_rpc_result({'some': 'result'}, None, 'MSGID')
    )


def test_is_response_with_request():
    assert not jsonrpc.is_response(jsonrpc.json_rpc_request('some_method'))


def test_is_response_with_notify():
    assert not jsonrpc.is_response(jsonrpc.json_rpc_notify('some_method'))


def test_is_request_with_result():
    assert not jsonrpc.is_request(
        jsonrpc.json_rpc_result({'some': 'result'}, None, 'MSGID')
    )


def test_is_request_with_notify():
    assert not jsonrpc.is_request(jsonrpc.json_rpc_notify('some_method'))


def test_is_request_with_request():
    assert jsonrpc.is_request(jsonrpc.json_rpc_request('some_method'))
