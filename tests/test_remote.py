import pytest

from geonotebook.kernel import Remote

@pytest.fixture
def r(mocker):

    protocols = [{'procedure': 'no_args',
                  'required': [],
                  'optional': []},
                 {'procedure': 'required_only',
                  'required': ["a", "b"],
                  'optional': []},
                 {'procedure': 'optional_only',
                  'required': [],
                  'optional': ["x", "y", "z"]},
                 {'procedure': 'required_and_optional',
                  'required': ["a", "b"],
                  'optional': ["x", "y", "z"]}]

    r = Remote(None, protocols)

    # Mock out the UUID.uuid4 function to return a consistent ID for testing
    mocker.patch('geonotebook.jsonrpc.uuid.uuid4', return_value='TEST-ID')

    mocker.patch.object(r, '_send_msg')
    return r

def test_remote_bad_protocol():
    with pytest.raises(AssertionError):
        Remote(None, ['foo', 'bar'])

def test_remote_bad_protocol_missing_procedure():
    with pytest.raises(AssertionError):
        Remote(None, [{'required': [],
                       'optional': []}])

def test_remote_bad_protocol_missing_required():
    with pytest.raises(AssertionError):
        Remote(None, [{'procedure': 'no_args',
                       'optional': []}])

def test_remote_bad_protocol_missing_optional():
    with pytest.raises(AssertionError):
        Remote(None, [{'procedure': 'no_args',
                       'required': []}])

def test_remote_init(r):
    assert hasattr(r.no_args, '__call__')
    assert hasattr(r.required_only, '__call__')
    assert hasattr(r.required_and_optional, '__call__')


def test_remote_call_no_args(r):
    r.no_args()
    assert r._send_msg.call_count == 1
    r._send_msg.assert_called_with({'jsonrpc': '2.0', 'params': [],
                                    'method': 'no_args', 'id': 'TEST-ID'})

def test_remote_call_no_args_with_args(r):
    with pytest.raises(AssertionError):
        r.no_args('foo', 'bar')


def test_remote_call_required_only(r):
    r.required_only('foo', 'bar')
    assert r._send_msg.call_count == 1
    r._send_msg.assert_called_with({'jsonrpc': '2.0', 'params': ['foo', 'bar'],
                                    'method': 'required_only', 'id': 'TEST-ID'})

def test_remote_call_required_only_with_too_few_args(r):
    with pytest.raises(AssertionError):
        r.no_args('foo')

def test_remote_call_required_only_with_too_many_args(r):
    with pytest.raises(AssertionError):
        r.no_args('foo', 'bar', 'baz')


def test_remote_call_optional_only(r):
    r.optional_only(x='foo', y='bar', z='baz')
    assert r._send_msg.call_count == 1
    r._send_msg.assert_called_with({'jsonrpc': '2.0', 'params': ['foo', 'bar', 'baz'],
                                    'method': 'optional_only', 'id': 'TEST-ID'})


    r.optional_only()
    assert r._send_msg.call_count == 2
    r._send_msg.assert_called_with({'jsonrpc': '2.0', 'params': [],
                                    'method': 'optional_only', 'id': 'TEST-ID'})

@pytest.mark.skip(reason="See: geonotebook/issues/45")
def test_remote_call_optional_only_missing_arguments():
    r.optional_only(x='foo', z='bar')
    assert r._send_msg.call_count == 3
    r._send_msg.assert_called_with({'jsonrpc': '2.0', 'params': ["???"],
                                    'method': 'optional_only', 'id': 'TEST-ID'})



def test_remote_promise_resolve_success(r):
    class nonlocal: pass

    def success(val):
        nonlocal.result = val

    def error(val):
        nonlocal.result = val

    p = r.no_args().then(success, error)
    r.resolve({'id': 'TEST-ID', 'result': 'SUCCESS', 'error': None})
    assert nonlocal.result == 'SUCCESS'

def test_remote_promise_resolve_error(r):
    class nonlocal: pass

    def success(val):
        nonlocal.result = val

    def error(val):
        nonlocal.result = val

    p = r.no_args().then(success, error)
    #import rpdb; rpdb.set_trace()

    r.resolve({'id': 'TEST-ID', 'result': None, 'error': 'ERROR'})

    assert isinstance(nonlocal.result, Exception)
    assert str(nonlocal.result) == "ERROR"


@pytest.mark.skip(reason="See: geonotebook/issues/46")
def test_remote_promise_resolve_with_bad_message(r, mocker):
    class nonlocal: pass

    def success(val):
        nonlocal.result = val

    def error(val):
        nonlocal.result = val

    p = r.no_args().then(success, error)
    with pytest.raises(Exception):
        r.resolve('bad message')

    p = r.no_args().then(success, error)
    with pytest.raises(Exception):
        r.resolve({'id': 'TEST-ID', 'bad': 'message'})

    p = r.no_args().then(success, error)

    warn = mocker.patch.object(r.log, 'warn')
    r.resolve({'id': 'BAD-ID'})
    assert warn.called_once == 1
