import pytest

from geonotebook.jsonrpc import Remote

@pytest.fixture
def remote(mocker):

    protocols = [{'procedure': 'no_args',
                  'required': [],
                  'optional': []},
                 {'procedure': 'required_only',
                  'required': [{"key": "a"}, {"key": "b"}],
                  'optional': []},
                 {'procedure': 'optional_only',
                  'required': [],
                  'optional': [{"key": "x"}, {"key": "y"}, {"key": "z"}]},
                 {'procedure': 'required_and_optional',
                  'required': [{"key": "a"}, {"key": "b"}],
                  'optional': [{"key": "x"}, {"key": "y"}, {"key": "z"}]}]

    r = Remote()
    r(None, protocols)

    # Mock out the UUID.uuid4 function to return a consistent ID for testing
    mocker.patch('geonotebook.jsonrpc.uuid.uuid4', return_value='TEST-ID')

    mocker.patch.object(r, '_send_msg')
    return r

def test_remote_bad_protocol():
    r = Remote()
    with pytest.raises(AssertionError):
        r(None, ['foo', 'bar'])

def test_remote_bad_protocol_missing_procedure():
    r = Remote()
    with pytest.raises(AssertionError):
        r(None, [{'required': [],
                  'optional': []}])

def test_remote_bad_protocol_missing_required():
    r = Remote()
    with pytest.raises(AssertionError):
        r(None, [{'procedure': 'no_args',
                  'optional': []}])

def test_remote_bad_protocol_missing_optional():
    r = Remote()
    with pytest.raises(AssertionError):
        r(None, [{'procedure': 'no_args',
                  'required': []}])

def test_remote_init(remote):
    assert hasattr(remote.no_args, '__call__')
    assert hasattr(remote.required_only, '__call__')
    assert hasattr(remote.required_and_optional, '__call__')


def test_remote_call_no_args(remote):
    remote.no_args()
    assert remote._send_msg.call_count == 1
    remote._send_msg.assert_called_with({'jsonrpc': '2.0', 'params': [],
                                    'method': 'no_args', 'id': 'TEST-ID'})

def test_remote_call_no_args_with_args(remote):
    with pytest.raises(AssertionError):
        remote.no_args('foo', 'bar')


def test_remote_call_required_only(remote):
    remote.required_only('foo', 'bar')
    assert remote._send_msg.call_count == 1
    remote._send_msg.assert_called_with({'jsonrpc': '2.0', 'params': [{'key': 'a',
                                                                  'value': 'foo',
                                                                  'required': True},
                                                                 {'key': 'b',
                                                                  'value': 'bar',
                                                                  'required': True}],
                                    'method': 'required_only', 'id': 'TEST-ID'})

def test_remote_call_required_only_with_too_few_args(remote):
    with pytest.raises(AssertionError):
        remote.required_only('foo')

def test_remote_call_required_only_with_too_many_args(remote):
    with pytest.raises(AssertionError):
        remote.no_args('foo', 'bar', 'baz')


def test_remote_call_optional_only(remote):
    remote.optional_only(x='foo', y='bar', z='baz')
    assert remote._send_msg.call_count == 1
    remote._send_msg.assert_called_with({'jsonrpc': '2.0', 'params': [{'key': 'x', 'value': 'foo', 'required': False},
                                                                 {'key': 'y', 'value': 'bar', 'required': False},
                                                                 {'key': 'z', 'value': 'baz', 'required': False}],
                                    'method': 'optional_only', 'id': 'TEST-ID'})


    remote.optional_only()
    assert remote._send_msg.call_count == 2
    remote._send_msg.assert_called_with({'jsonrpc': '2.0', 'params': [],
                                    'method': 'optional_only', 'id': 'TEST-ID'})

def test_remote_call_optional_only_missing_arguments(remote):
    remote.optional_only(x='foo', z='bar')
    assert remote._send_msg.call_count == 1
    remote._send_msg.assert_called_with({'jsonrpc': '2.0', 'params': [{'key': 'x', 'value': 'foo', 'required': False},
                                                                 {'key': 'z', 'value': 'bar', 'required': False}],
                                    'method': 'optional_only', 'id': 'TEST-ID'})



def test_remote_promise_resolve_success(remote):
    class Nonlocal(object): pass

    def success(val):
        Nonlocal.result = val

    def error(val):
        Nonlocal.result = val

    p = remote.no_args().then(success, error)
    remote.resolve({'id': 'TEST-ID', 'result': 'SUCCESS', 'error': None})
    assert Nonlocal.result == 'SUCCESS'

def test_remote_promise_resolve_error(remote):
    class Nonlocal(object): pass

    def success(val):
        Nonlocal.result = val

    def error(val):
        Nonlocal.result = val

    p = remote.no_args().then(success, error)
    #import rpdb; rpdb.set_trace()

    remote.resolve({'id': 'TEST-ID', 'result': None, 'error': 'ERROR'})

    assert isinstance(Nonlocal.result, Exception)
    assert str(Nonlocal.result) == "ERROR"


@pytest.mark.skip(reason="See: geonotebook/issues/46")
def test_remote_promise_resolve_with_bad_message(r, mocker):
    class Nonlocal(object): pass

    def success(val):
        Nonlocal.result = val

    def error(val):
        Nonlocal.result = val

    p = remote.no_args().then(success, error)
    with pytest.raises(Exception):
        remote.resolve('bad message')

    p = remote.no_args().then(success, error)
    with pytest.raises(Exception):
        remote.resolve({'id': 'TEST-ID', 'bad': 'message'})

    p = remote.no_args().then(success, error)

    warn = mockeremote.patch.object(remote.log, 'warn')
    remote.resolve({'id': 'BAD-ID'})
    assert warn.called_once == 1
