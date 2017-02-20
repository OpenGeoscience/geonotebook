import _ from 'underscore';

import Map from 'ol/map';
import View from 'ol/view';
import TileLayer from 'ol/layer/tile';
import XYZ from 'ol/source/xyz';
import TileWMS from 'ol/source/tilewms';
import Attribution from 'ol/attribution';

import annotate from './jsonrpc/annotate';
import constants from './jsonrpc/constants';

var MapObject = function (notebook) {
  this.notebook = notebook;
  this.olmap = null;
  this.region = null;
  this.annotation_color_palette = [
    '#db5f57', // {r:219, g: 95, b: 87}
    '#dbae57', // {r:219, g:174, b: 87}
    '#b9db57', // {r:185, g:219, b: 87}
    '#69db57', // {r:105, g:219, b: 87}
    '#57db94', // {r: 87, g:219, b:148}
    '#57d3db', // {r: 87, g:211, b:219}
    '#5784db', // {r: 87, g:132, b:219}
    '#7957db', // {r:121, g: 87, b:219}
    '#c957db', // {r:201, g: 87, b:219}
    '#db579e'  // {r:219, g: 87, b:158}
  ];
  this._color_counter = -1;
};

MapObject.prototype.next_color = function () {
  this._color_counter = this._color_counter + 1;

  var idx = this._color_counter % this.annotation_color_palette.length;

  return this.annotation_color_palette[idx];
};

MapObject.prototype.init_map = function () {
  $('#geonotebook-map').empty();
  this.olmap = new Map({
    target: 'geonotebook-map',
    view: new View({
      center: [0, 0],
      zoom: 2
    })
  });
  this._layers = {};
};

/**
 * Force the map object to resize itself when layouts change.
 */
MapObject.prototype.resize = function () {
  var node = $(this.olmap.getViewport());
  this.olmap.setSize([node.width(), node.height()]);
};

MapObject.prototype.rpc_error = function (error) {
  console.log('JSONRPCError(' + error.code + '): ' + error.message); // eslint-disable-line no-console
};

MapObject.prototype.msg_types = [
  'get_protocol',
  'set_center',
  '_debug',
  'add_layer',
  'replace_layer',
  'replace_wms_layer',
  'add_osm_layer',
  'add_annotation_layer',
  'clear_annotations',
  'remove_layer',
  'add_annotation',
  'add_vector_layer'
];

MapObject.prototype._debug = function (msg) {
  console.log(msg); // eslint-disable-line no-console
};

// Generate a list of protocol definitions for the white listed functions
// in msg_types. This will be passed to the Python geonotebook object and
// will initialize its RPC object so JS map frunctions can be called from
// the Python environment.

MapObject.prototype.get_protocol = function () {
  return _.map(this.msg_types, (msg_type) => {
    var args = annotate(this[msg_type]);

    return {
      procedure: msg_type,
      required: args.filter(function (arg) { return !arg.default; }),
      optional: args.filter(function (arg) { return !!arg.default; })
    };
  });
};

MapObject.prototype.set_center = function (x, y, z) {
  if (x < -180.0 || x > 180.0 || y < -90.0 || y > 90.0) {
    throw new constants.InvalidParams('Invalid parameters sent to set_center!');
  }
  var view = this.olmap.getView();
  view.setCenter([x, y]);
  view.setZoom(z);

  return [x, y, z];
};

MapObject.prototype.get_layer = function (layer_name) {
  return this._layers[layer_name];
};

MapObject.prototype.remove_layer = function (layer_name) {
  var layer = this._layers[layer_name];
  if (!layer) {
    return null;
  }

  this.olmap.removeLayer(layer);
  delete this._layers[layer_name];
  return layer_name;
};

MapObject.prototype.clear_annotations = function () {
};

MapObject.prototype.add_annotation = function (type, args, kwargs) {
};

MapObject.prototype._add_annotation_handler = function (annotation) {
};

MapObject.prototype.state_annotation_handler = function (evt) {
};

MapObject.prototype.add_annotation_layer = function (layer_name) {
  return layer_name;
};

MapObject.prototype._set_layer_zindex = function (layer, index) {
};

MapObject.prototype.add_layer = function (layer_name, vis_url, vis_params, query_params) {
  var layer_type = vis_params['layer_type'];

  if (layer_type === 'annotation') {
    return this.add_annotation_layer(layer_name);
  } else if (layer_type === 'osm') {
    return this.add_osm_layer(layer_name, vis_url, vis_params, query_params);
  } else if (layer_type === 'wms') {
    return this.add_wms_layer(layer_name, vis_url, vis_params, query_params);
  } else if (layer_type === 'vector') {
    return this.add_vector_layer(layer_name, vis_url, vis_params, query_params);
  } else {
    return this.add_default_layer(layer_name, vis_url, vis_params, query_params);
  }
};

MapObject.prototype.replace_layer = function (prev_layer, layer_name, vis_url, vis_params, query_params) {
};

MapObject.prototype.add_osm_layer = function (layer_name, url, vis_params, query_params) {
  this._baseLayer = this.olmap.addLayer(new TileLayer({
    source: new XYZ({
      url: url.replace('{s}', 'a'),
      attributions: new Attribution({
        html: vis_params.attribution || ''
      })
    })
  }));

  return layer_name;
};

MapObject.prototype.add_default_layer = function (layer_name, base_url, vis_params, query_params) {
  var params = $.param(query_params || {});

  var layer = this.olmap.addLayer(new TileLayer({
    source: new XYZ({
      url: base_url + '/{x}/{y}/{z}.png?' + params
    })
  }));
  this._layers[layer_name] = layer;
  return layer_name;
};

MapObject.prototype.add_wms_layer = function (layer_name, base_url, query_params) {
  var layer = this.olmap.addLayer(new TileLayer({
    source: new TileWMS({
      url: base_url,
      params: {
        TILED: true
      }
    })
  }));
  this._layers[layer_name] = layer;
  return layer_name;
};

MapObject.prototype.add_vector_layer = function (name, data, vis_params, query_params) {
  return name;
};

export default MapObject;
