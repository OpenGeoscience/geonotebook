import os
import pytest
from geonotebook import layers, wrappers
import mock
from pytest_mock import mocker

DEFAULT_CONFIG = """
[default]
vis_server = geoserver

[geoserver]
username = admin
password = geoserver
url = http://0.0.0.0:8080/geoserver
"""

@pytest.fixture(autouse=True)
def geonotebook_ini(tmpdir):
    p = tmpdir.mkdir('config').join("geonotebook.ini")
    p.write(DEFAULT_CONFIG)
    os.environ["GEONOTEBOOK_INI"] = str(p)

@pytest.fixture
def geoserver(mocker, monkeypatch):
    import geonotebook
    geoserver = mocker.patch('geonotebook.vis.geoserver.geoserver.Geoserver')
    monkeypatch.setitem(geonotebook.config.Config._valid_vis_hash, 'geoserver', geoserver)
    return geoserver.return_value


def test_layer_reprs(geoserver):
    assert str(layers.GeonotebookLayer('gnbl', None)) == "<GeonotebookLayer('gnbl')>"
    assert str(layers.AnnotationLayer('al', None, None)) == "<AnnotationLayer('al')>"
    assert str(layers.NoDataLayer('ndl', None, None)) == "<NoDataLayer('ndl')>"
    assert str(layers.DataLayer('dl', None, None, vis_url='bogus')) == "<DataLayer('dl')>"
    assert str(layers.SimpleLayer('sl', None, None, vis_url='bogus')) == "<SimpleLayer('sl')>"
    assert str(layers.TimeSeriesLayer('tsl', None, [mock.Mock(name='bogus_data')])) == \
        "<TimeSeriesLayer('tsl')>"
