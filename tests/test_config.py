import os
import sys
import tempfile

import pytest
import six

from geonotebook import config

config_paths = {
    "/etc/geonotebook.ini": None,
    "/usr/etc/geonotebook.ini": None,
    "/usr/local/etc/geonotebook.ini": None,
    os.path.join(sys.prefix, "etc/geonotebook.ini"): None,
    os.path.expanduser("~/.geonotebook.ini"): None,
    os.path.join(os.getcwd(), ".geonotebook.ini"): None,
    os.path.expandvars("${GEONOTEBOOK_INI}"): None
}


def make_config(settings):
    """Generate a config file string from a settings object."""
    s = ''
    for section, defs in six.iteritems(settings):
        s += '[%s]\n' % section
        for key, value in six.iteritems(defs):
            s += '%s = %s\n' % (key, value)
    return s


def mock_file(content):
    """Generate a file like object containing the given content."""
    temp = tempfile.TemporaryFile()
    temp.write(content)
    temp.seek(0)
    return temp


class MockFileOpener(object):
    """Mock the builtin open object.

    Takes a single object as an argument.  The keys
    of this object are a list of files handled by the
    mocked open method.  The value of each key is a string
    that is passed back to the ``read`` method.
    """

    def __init__(self, files=None):
        if files is None:
            files = {}
        self.files = files
        self._open = six.moves.builtins.open

    def open(self, name, mode='r', **kwargs):
        if name not in self.files:
            return self._open(name, mode, **kwargs)

        if mode != 'r':
            raise Exception('Mocked files are read only')

        if self.files[name] is None:
            raise IOError(name)

        return mock_file(self.files[name])


@pytest.fixture
def mockopen(monkeypatch):
    manager = MockFileOpener()
    monkeypatch.setattr(six.moves.builtins, 'open', manager.open)
    return manager


@pytest.fixture
def mockconfig(mockopen):
    files = {}
    files.update(config_paths)
    mockopen.files = files
    return mockopen


def test_no_config_file(mockconfig):
    with pytest.raises(RuntimeError):
        config.Config()


def test_override_config(mockconfig):
    mockconfig.files['/etc/geonotebook.ini'] = make_config({
        'basemap': {
            'url': 'url a',
            'attribution': 'attribution a'
        }
    })

    mockconfig.files['/usr/etc/geonotebook.ini'] = make_config({
        'basemap': {
            'url': 'url b',
            'attribution': 'attribution b'
        }
    })

    mockconfig.files['/usr/local/etc/geonotebook.ini'] = make_config({
        'basemap': {
            'attribution': 'attribution c'
        }
    })

    mockconfig.files[
        os.path.expanduser('~/.geonotebook.ini')
    ] = make_config({
        'basemap': {
            'attribution': 'attribution d'
        }
    })

    c = config.Config()
    assert c.basemap == {'url': 'url b', 'attribution': 'attribution d'}


def test_custom_path(mockconfig):
    mockconfig.files['foo.ini'] = make_config({
        'test': {
            'foo': 'bar'
        }
    })

    c = config.Config(path='foo.ini')
    assert c.config.get('test', 'foo') == 'bar'


def test_vis_server_geoserver(mockconfig):
    mockconfig.files['/etc/geonotebook.ini'] = make_config({
        'default': {
            'vis_server': 'geoserver'
        },
        'geoserver': {
            'username': 'admin',
            'password': 'geoserver',
            'url': 'http://localhost'
        }
    })

    c = config.Config()
    assert c.vis_server.base_url == 'http://localhost'


def test_vis_server_invalid(mockconfig):
    mockconfig.files['/etc/geonotebook.ini'] = make_config({
        'default': {
            'vis_server': 'invalid'
        }
    })

    c = config.Config()
    with pytest.raises(NotImplementedError):
        c.vis_server
