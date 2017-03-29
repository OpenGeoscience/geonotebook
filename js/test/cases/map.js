import sinon from 'sinon';
import expect from 'expect.js';
import _ from 'underscore';

import MapObject from 'geonotebook/map/base';

/**
 * Create a mock map implementation for testing the
 * map renderer API.
 */
class MockImplementation extends MapObject {
  constructor () {
    const api = [
      '_init_map',
      '_resize',
      '_set_center',
      '_add_annotation_layer',
      '_add_osm_layer',
      '_add_wms_layer',
      '_add_vector_layer',
      '_add_tiled_layer',
      '_remove_layer',
      '_add_annotation',
      '_clear_annotations',
      '_trigger_draw'
    ];
    super({
      _remote: {
        add_annotation_from_client: sinon.stub().returns(Promise.resolve({}))
      }
    });
    _.each(api, (method) => {
      this[method] = sinon.stub();
    });
  }
}

describe('base map object', () => {
  var map;
  beforeEach(() => {
    $('<div id=geonotebook-map/>').addClass('mocked-map')
      .css({
        width: '600px',
        height: '400px'
      })
      .appendTo('body');
    map = new MockImplementation();
    sinon.stub(console, 'log');
  });
  afterEach(() => {
    $('#geonotebook-map').remove();
    console.log.restore();
  });

  it('node', () => {
    expect($(map.node).hasClass('mocked-map')).to.be(true);
  });

  it('init_map', () => {
    expect(map.init_map()).to.be(true);
    sinon.assert.calledOnce(map._init_map);
  });

  describe('set_center', () => {
    it('valid', () => {
      map._set_center.returns([1, 2, 3]);
      expect(map.set_center(4, 5, 6)).to.eql([1, 2, 3]);
      sinon.assert.calledOnce(map._set_center);
      sinon.assert.calledWith(map._set_center, 4, 5, 6);
    });

    it('invalid', () => {
      expect(map.set_center).withArgs(0, 0, -1).to.throwException();
      expect(map.set_center).withArgs(-10000, 0, 0).to.throwException();
      expect(map.set_center).withArgs(0, 10000, 0).to.throwException();
    });
  });

  describe('add_layer', () => {
    it('annotation', () => {
      const params = {
        layer_type: 'annotation'
      };
      map._add_annotation_layer.returns('layer object');

      expect(
        map.add_layer('a', 'url', params, 'query')
      ).to.be('a');

      // check delegation to _add_annotation_layer
      sinon.assert.calledOnce(map._add_annotation_layer);
      sinon.assert.calledWith(map._add_annotation_layer, 'a');

      // check layers are auto removed
      expect(
        map.add_layer('a', 'url', params, 'query')
      ).to.be('a');
      sinon.assert.calledOnce(map._remove_layer);
      sinon.assert.calledWith(map._remove_layer, 'a');
    });

    it('wms', () => {
      const params = {
        layer_type: 'wms'
      };
      map._add_wms_layer.returns('layer object');

      expect(
        map.add_layer('a', 'url', params, 'query')
      ).to.be('a');

      // check delegation to _add_wms_layer
      sinon.assert.calledOnce(map._add_wms_layer);
      sinon.assert.calledWith(map._add_wms_layer, 'a');

      // check layers are auto removed
      expect(
        map.add_layer('a', 'url', params, 'query')
      ).to.be('a');
      sinon.assert.calledOnce(map._remove_layer);
      sinon.assert.calledWith(map._remove_layer, 'a');
    });

    it('osm', () => {
      const params = {
        layer_type: 'osm'
      };
      map._add_osm_layer.returns('layer object');

      expect(
        map.add_layer('a', 'url', params, 'query')
      ).to.be('a');

      // check delegation to _add_osm_layer
      sinon.assert.calledOnce(map._add_osm_layer);
      sinon.assert.calledWith(map._add_osm_layer, 'a');

      // check layers are auto removed
      expect(
        map.add_layer('a', 'url', params, 'query')
      ).to.be('a');
      sinon.assert.calledOnce(map._remove_layer);
      sinon.assert.calledWith(map._remove_layer, 'a');
    });

    it('vector', () => {
      const params = {
        layer_type: 'vector'
      };
      map._add_vector_layer.returns('layer object');

      expect(
        map.add_layer('a', 'url', params, 'query')
      ).to.be('a');

      // check delegation to _add_vector_layer
      sinon.assert.calledOnce(map._add_vector_layer);
      sinon.assert.calledWith(map._add_vector_layer, 'a');

      // check layers are auto removed
      expect(
        map.add_layer('a', 'url', params, 'query')
      ).to.be('a');
      sinon.assert.calledOnce(map._remove_layer);
      sinon.assert.calledWith(map._remove_layer, 'a');
    });

    it('default', () => {
      const params = {};
      map._add_tiled_layer.returns('layer object');

      expect(
        map.add_layer('a', 'url', params, 'query')
      ).to.be('a');

      // check delegation to _add_tiled_layer
      sinon.assert.calledOnce(map._add_tiled_layer);
      sinon.assert.calledWith(map._add_tiled_layer, 'a');

      // check layers are auto removed
      expect(
        map.add_layer('a', 'url', params, 'query')
      ).to.be('a');
      sinon.assert.calledOnce(map._remove_layer);
      sinon.assert.calledWith(map._remove_layer, 'a');
    });

    it('invalid', () => {
      const params = {};
      map._add_tiled_layer.returns(null);

      expect(
        map.add_layer('a', 'url', params, 'query')
      ).to.be('a');

      // check delegation to _add_tiled_layer
      sinon.assert.calledOnce(map._add_tiled_layer);
      sinon.assert.calledWith(map._add_tiled_layer, 'a');

      // check that the layer was not actually added
      expect(map.layers).to.not.have.key('a');
    });
  });

  it('add_annotation_layer', () => {
    map._add_annotation_layer.returns('layer object');

    expect(
      map.add_annotation_layer('a')
    ).to.be('a');

    // check delegation to _add_annotation_layer
    sinon.assert.calledOnce(map._add_annotation_layer);
    sinon.assert.calledWith(map._add_annotation_layer, 'a');
  });

  it('update_layer', () => {
    const params = {};
    map._add_tiled_layer.returns('layer object');

    // generate an initial layer
    expect(
      map.add_layer('a', 'url', params, 'query')
    ).to.be('a');

    sinon.assert.calledOnce(map._add_tiled_layer);
    sinon.assert.calledWith(map._add_tiled_layer, 'a', 'url', params, 'query');

    map._add_tiled_layer.reset();
    map._add_tiled_layer.returns('other layer');

    // update the layer with new properties and validate
    expect(
      map.update_layer('a', 'other url', params, 'other query')
    ).to.be('a');
    sinon.assert.calledOnce(map._add_tiled_layer);
    sinon.assert.calledWith(map._add_tiled_layer, 'a', 'other url', params, 'other query');
    expect(map.layers.a).to.be('other layer');
  });

  it('get_layer', () => {
    const params = {};
    map._add_tiled_layer.returns('layer object');

    // generate an initial layer
    expect(
      map.add_layer('a', 'url', params, 'query')
    ).to.be('a');

    sinon.assert.calledOnce(map._add_tiled_layer);
    sinon.assert.calledWith(map._add_tiled_layer, 'a', 'url', params, 'query');

    expect(map.get_layer('a')).to.be('layer object');
    expect(map.get_layer('b')).to.be(null);
  });

  describe('add_annotation', () => {
    it('point', () => {
      const type = 'point';
      const args = [[1, 2]];
      const kwargs = {
        id: 'a',
        rgb: '#ff0000',
        name: 'annotation'
      };

      expect(
        map.add_annotation(type, args, kwargs)
      ).to.eql({
        id: kwargs.id,
        name: kwargs.name,
        rgb: kwargs.rgb
      });

      sinon.assert.calledOnce(
        map._add_annotation
      );
      sinon.assert.calledWith(
        map._add_annotation,
        'point', sinon.match({
          type: 'Feature',
          geometry: sinon.match({
            type: 'Point',
            coordinates: args[0]
          }),
          properties: sinon.match({
            name: kwargs.name,
            rgb: kwargs.rgb
          }),
          id: kwargs.id
        })
      );
    });

    it('rectangle', () => {
      const type = 'rectangle';
      const args = [[[0, 0], [0, 2], [1, 2], [1, 0], [0, 0]]];
      const kwargs = {
        id: 'a',
        rgb: '#ff0000',
        name: 'annotation'
      };

      expect(
        map.add_annotation(type, args, kwargs)
      ).to.eql({
        id: kwargs.id,
        name: kwargs.name,
        rgb: kwargs.rgb
      });

      sinon.assert.calledOnce(
        map._add_annotation
      );
      sinon.assert.calledWith(
        map._add_annotation,
        'rectangle', sinon.match({
          type: 'Feature',
          geometry: sinon.match({
            type: 'Polygon',
            coordinates: args
          }),
          properties: sinon.match({
            name: kwargs.name,
            rgb: kwargs.rgb
          }),
          id: kwargs.id
        })
      );
    });

    it('invalid', () => {
      expect(map.add_annotation).withArgs('foo', [], {}).to.throwException();
    });

    it('no id', () => {
      const type = 'point';
      const args = [[1, 2]];
      const kwargs = {
        rgb: '#ff0000',
        name: 'annotation'
      };

      expect(
        map.add_annotation(type, args, kwargs).id
      ).to.match(/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/i);
    });

    it('no color', () => {
      const type = 'point';
      const args = [[1, 2]];
      const kwargs = {
        id: 'a',
        name: 'annotation'
      };

      expect(
        map.add_annotation(type, args, kwargs).rgb
      ).to.match(/#[0-9a-f]{6}/i);
    });

    it('no name', () => {
      const type = 'point';
      const args = [[1, 2]];
      const kwargs = {
        id: 'a',
        rgb: '#ff00ff'
      };

      expect(
        map.add_annotation(type, args, kwargs).name
      ).to.match(/^point .*/);
    });
  });

  it('clear_annotations', () => {
    expect(map.clear_annotations()).to.be(true);
    sinon.assert.calledOnce(map._clear_annotations);
  });

  it('trigger_draw', () => {
    map.trigger_draw();
    sinon.assert.calledOnce(map._trigger_draw);
  });

  it('resize', () => {
    expect(
      map.resize()
    ).to.eql({
      width: 600,
      height: 400
    });

    sinon.assert.calledOnce(map._resize);
    sinon.assert.calledWith(map._resize, {width: 600, height: 400});
  });

  it('get_protocol', () => {
    const protocol = map.get_protocol();
    expect(_.pluck(protocol, 'procedure')).to.eql(map.msg_types);
  });

  it('on_add_annotation', () => {
    return map.on_add_annotation('point', 'coordinates', 'meta')
      .then(() => {
        sinon.assert.calledOnce(console.log);
        sinon.assert.calledWith(console.log, 'annotation added');

        sinon.assert.calledOnce(map.notebook._remote.add_annotation_from_client);
        sinon.assert.calledWith(
          map.notebook._remote.add_annotation_from_client,
          'point', 'coordinates', 'meta'
        );
      });
  });

  it('rpc_error', () => {
    map.rpc_error('an error');
    sinon.assert.calledOnce(console.log);
    sinon.assert.calledWith(console.log, sinon.match(/^JSONRPCError\(.*/));
  });

  it('debug', () => {
    map.debug('a message');
    sinon.assert.calledOnce(console.log);
    sinon.assert.calledWith(console.log, 'a message');
  });
});
