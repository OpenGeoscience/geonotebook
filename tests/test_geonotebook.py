import pytest

from geonotebook.kernel import Geonotebook


@pytest.fixture
def nbclass():
    class MockNotebook(Geonotebook):
        msg_types = ['no_args', 'required_only', 'kw_only',
                     'mixed', 'varargs', 'kwargs']

        def no_args(self):
            pass

        def required_only(self, x, y, z):
            pass

        def kw_only(self, foo=10, bar=20):
            pass

        def mixed(self, x, y, foo=10, bar=20):
            pass

        def varargs(self, *args):
            pass

        def kwargs(self, **kwargs):
            pass

    return MockNotebook


@pytest.fixture
def nbprotocol(nbclass):
    return nbclass.class_protocol()


@pytest.fixture
def nbprotocoldict(nbprotocol):
    return {p['procedure']: p for p in nbprotocol}


@pytest.fixture
def no_args(nbprotocoldict):
    return nbprotocoldict['no_args']


@pytest.fixture
def required_only(nbprotocoldict):
    return nbprotocoldict['required_only']


@pytest.fixture
def kw_only(nbprotocoldict):
    return nbprotocoldict['kw_only']


@pytest.fixture
def mixed(nbprotocoldict):
    return nbprotocoldict['mixed']


@pytest.fixture
def varargs(nbprotocoldict):
    return nbprotocoldict['varargs']


@pytest.fixture
def kwargs(nbprotocoldict):
    return nbprotocoldict['kwargs']


# Tests

def test_class_protocol(nbprotocol):
    assert len(nbprotocol) == 6


def test_protocol_keys(nbprotocol):
    for p in nbprotocol:
        assert 'procedure' in p
        assert 'required' in p
        assert 'optional' in p


def test_protocols_match_msg_types(nbclass):
    assert set(nbclass.msg_types) == \
        set([p['procedure'] for p in nbclass.class_protocol()])


def test_protocol_required_params_no_args(no_args):
    assert len(no_args['required']) == 0


def test_protocol_required_params_varargs(varargs):
    assert len(varargs['required']) == 0


def test_protocol_required_params_kwargs(kwargs):
    assert len(kwargs['required']) == 0


def test_protocol_required_params_required_only(required_only):
    reqs = required_only['required']
    assert len(reqs) == 3
    for r in reqs:
        assert 'key' in r
        assert 'default' in r
        assert r['default'] is False
    assert reqs[0]['key'] == 'x'
    assert reqs[1]['key'] == 'y'
    assert reqs[2]['key'] == 'z'


def test_protocol_required_params_mixed(mixed):
    reqs = mixed['required']
    assert len(reqs) == 2
    for r in reqs:
        assert 'key' in r
        assert 'default' in r
        assert r['default'] is False
    assert reqs[0]['key'] == 'x'
    assert reqs[1]['key'] == 'y'


def test_protocol_optional_params_no_args(no_args):
    assert len(no_args['optional']) == 0


def test_protocol_optional_params_required_only(required_only):
    assert len(required_only['optional']) == 0


def test_protocol_optional_params_varargs(varargs):
    assert len(varargs['optional']) == 0


def test_protocol_optional_params_kwargs(kwargs):
    assert len(kwargs['optional']) == 0


def test_protocol_optional_params_kw_only(kw_only):
    ops = kw_only['optional']
    assert len(ops) == 2
    for o in ops:
        assert 'key' in o
        assert 'default' in o
    assert ops[0]['key'] == 'foo'
    assert ops[0]['default'] == 10
    assert ops[1]['key'] == 'bar'
    assert ops[1]['default'] == 20


def test_protocol_optional_params_mixed(mixed):
    ops = mixed['optional']
    assert len(ops) == 2
    for o in ops:
        assert 'key' in o
        assert 'default' in o
    assert ops[0]['key'] == 'foo'
    assert ops[0]['default'] == 10
    assert ops[1]['key'] == 'bar'
    assert ops[1]['default'] == 20
