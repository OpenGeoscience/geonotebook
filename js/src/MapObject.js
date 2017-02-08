import _ from 'underscore';
import 'geojs';

import GeoMap from 'geojs/map';
import JsonReader from 'geojs/jsonReader';
import event from 'geojs/event';
import { pointAnnotation, rectangleAnnotation, polygonAnnotation } from 'geojs/annotation';
import { transformCoordinates } from 'geojs/transform';
import annotate from './jsonrpc/annotate';
import constants from './jsonrpc/constants';

var geo_event = event;
var MapObject = function (notebook) {
  this.notebook = notebook;
  this.geojsmap = null;
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
  this.geojsmap = GeoMap({node: '#geonotebook-map',
    width: $('#geonotebook-map').width(),
    height: $('#geonotebook-map').height(),
    allowRotation: false
  });

    // this.geojsmap.geoOn('geo_select', this.geo_select.bind(this));
};

/**
 * Force the map object to resize itself when layouts change.
 */
MapObject.prototype.resize = function () {
  var node = $(this.geojsmap.node());
  this.geojsmap.size({
    width: node.width(),
    height: node.height()
  });
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
  this.geojsmap.center({x: x, y: y});
  this.geojsmap.zoom(z);

  return [x, y, z];
};

MapObject.prototype.get_layer = function (layer_name) {
  return _.find(this.geojsmap.layers(),
                  function (l) { return l.name() === layer_name; });
};

MapObject.prototype.remove_layer = function (layer_name) {
  this.geojsmap.deleteLayer(this.get_layer(layer_name));
  return layer_name;
};

MapObject.prototype.clear_annotations = function () {
  var annotation_layer = this.get_layer('annotation');
  this._color_counter = -1;
  return annotation_layer.removeAllAnnotations();
};

MapObject.prototype.add_annotation = function (type, args, kwargs) {
  if (_.contains(['point', 'rectangle', 'polygon'], type)) {
    var annotation_layer = this.get_layer('annotation');
    this._color_counter++;
  }

  var style = {
    fillColor: kwargs.rgb || this.next_color(),
    fillOpacity: 0.8,
    strokeWidth: 2
  };

  /*
   * This is an ugly hack to get around the fact that geojs doesn't return
   * the created annotation object.  Currently, the only way to get this
   * object is to listen to an event that also fires when generating annotations
   * with the mouse.  Further, the events are not fired consistently:
   *
   *  * When creating an annotation with the mouse, it is only triggered with state
   *    with mode `create` before it has any coordinate information.  No event
   *    add event is triggered after the annotation is finished.
   *  * When creating via the API, it is only triggered with state `done`.
   *
   * The code here expects this event will be triggered synchronously.  This is
   * currently true, but may change in the future.
   */
  var annotation;
  function _handler (evt) {
    annotation = evt.annotation;
  }
  annotation_layer.geoOn(geo_event.annotation.add, _handler);

  if (type === 'point') {
    annotation_layer.addAnnotation(pointAnnotation({
      position: transformCoordinates(this.geojsmap.ingcs(), this.geojsmap.gcs(), {
        x: args[0][0],
        y: args[0][1]
      }),
      style: style
    }));
  } else if (type === 'rectangle') {
    annotation_layer.addAnnotation(rectangleAnnotation({
      corners: _.map(args[0], (coords) => {
        return transformCoordinates(this.geojsmap.ingcs(), this.geojsmap.gcs(), {
          x: coords[0],
          y: coords[1]
        });
      }),
      style: style
    }));
  } else if (type === 'polygon') {
    annotation_layer.addAnnotation(polygonAnnotation({
      vertices: _.map(args[0], (coords) => {
        return transformCoordinates(this.geojsmap.ingcs(), this.geojsmap.gcs(), {
          x: coords[0],
          y: coords[1]
        });
      }),
      style: style
    }));
  } else {
    console.error('Attempting to add annotation of type ' + type);
    return false;
  }
  annotation_layer.geoOff(geo_event.annotation.add, _handler);

  if (!annotation) {
    console.error('GeoJS did not respond with a synchronous annotation event.');
    return false;
  }

  if (kwargs.name) {
    annotation.name(kwargs.name);
  }

  return {
    id: annotation.id(),
    name: annotation.name(),
    rgb: style.fillColor
  };
};

MapObject.prototype._map_coordinates = function (coordinates, type) {
  if (type === 'point') {
    return [coordinates[0].x, coordinates[0].y];
  }
  return _.map(coordinates, (c) => {
    return [c.x, c.y];
  });
};

MapObject.prototype._add_annotation_handler = function (annotation) {
  annotation.options('style').fillColor = this.next_color();
  annotation.options('style').fillOpacity = 0.8;
  annotation.options('style').strokeWidth = 2;

  var annotation_meta = {
    id: annotation.id(),
    name: annotation.name(),
    rgb: annotation.options('style').fillColor
  };

  var coordinates = this._map_coordinates(
    annotation.coordinates('EPSG:4326'),
    annotation.type()
  );

  this.notebook._remote.add_annotation_from_client(
        annotation.type(),
        coordinates,
        annotation_meta
    ).then(
        function () {
          annotation.layer().modified();
          annotation.draw();
        },
        this.rpc_error.bind(this));
};

MapObject.prototype.state_annotation_handler = function (evt) {
  var annotation = evt.annotation;
  if (_.contains(['point', 'polygon', 'rectangle'], annotation.type())) {
    this._add_annotation_handler(annotation);
  }
};

MapObject.prototype.add_annotation_layer = function (layer_name) {
  var layer = this.geojsmap.createLayer('annotation', {
    annotations: ['rectangle', 'point', 'polygon']
  });
  layer.name(layer_name);

//            layer.geoOn(geo_event.annotation.remove, handleAnnotationChange);
  layer.geoOn(geo_event.annotation.state, this.state_annotation_handler.bind(this));

  layer.geoOn('geonotebook:rectangle_annotation_mode', function () {
    layer.mode('rectangle');
  });

  layer.geoOn('geonotebook:point_annotation_mode', function () {
    layer.mode('point');
  });

  layer.geoOn('geonotebook:polygon_annotation_mode', function () {
    layer.mode('polygon');
  });

  return layer_name;
};

MapObject.prototype._set_layer_zindex = function (layer, index) {
  if (index !== undefined) {
    var annotation_layer = this.get_layer('annotation');
    layer.zIndex(index);
    if (annotation_layer !== undefined) {
            // Annotation layer should always be on top
      var max = _.max(_.invoke(this.geojsmap.layers(), 'zIndex'));
      annotation_layer.zIndex(max + 1);
    }
  }
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
  var old_layer = _.find(this.geojsmap.layers(), function (e) { return e.name() === prev_layer; });

  if (old_layer === undefined) {
    console.log('Could not find ' + layer_name + ' layer'); // eslint-disable-line no-console
    return false;
  } else {
    // Set the zIndex
    query_params['zIndex'] = old_layer.zIndex();
    // Delete the Layer
    this.geojsmap.deleteLayer(this.get_layer(old_layer.name()));
    // Add the new layer
    return this.add_layer(layer_name, vis_url, vis_params, query_params);
  }
};

MapObject.prototype.add_osm_layer = function (layer_name, url, vis_params, query_params) {
  var opts = {};
  if (vis_params.attribution) {
    opts.attribution = vis_params.attribution;
  }
  var osm = this.geojsmap.createLayer('osm', opts);

  osm.name(layer_name);
  osm.url(url);

    // make sure zindex is explicitly set
  this._set_layer_zindex(osm, vis_params['zIndex']);

  return layer_name;
};

MapObject.prototype.add_default_layer = function (layer_name, base_url, vis_params, query_params) {
    // If a layer with this name already exists,  replace it
  if (this.get_layer(layer_name) !== undefined) {
    this.geojsmap.deleteLayer(this.get_layer(layer_name));
  }

  var wms = this.geojsmap.createLayer('osm', {
    keepLower: false,
    attribution: null
  });

    // make sure zindex is explicitly set
  this._set_layer_zindex(wms, vis_params['zIndex']);

  wms.name(layer_name);

  var param_string = '';
  if ($.param(query_params)) {
    param_string = '?' + $.param(query_params);
  }

  wms.url(function (x, y, zoom) {
    return base_url + '/' + x + '/' + y + '/' + zoom + '.png' + param_string;
  });

  return layer_name;
};

MapObject.prototype.add_wms_layer = function (layer_name, base_url, query_params) {
    // If a layer with this name already exists,  replace it
  if (this.get_layer(layer_name) !== undefined) {
    this.geojsmap.deleteLayer(this.get_layer(layer_name));
  }

  var projection = query_params['projection'] || 'EPSG:3857';

  var wms = this.geojsmap.createLayer('osm', {
    keepLower: false,
    attribution: null
  });

    // make sure zindex is explicitly set
  this._set_layer_zindex(wms, query_params['zIndex']);

  wms.name(layer_name);

  wms.url(function (x, y, zoom) {
    var bb = wms.gcsTileBounds({
      x: x,
      y: y,
      level: zoom
    }, projection);

    var bbox_mercator = bb.left + ',' + bb.bottom + ',' +
                 bb.right + ',' + bb.top;

    var local_params = {
      'SERVICE': 'WMS',
      'VERSION': '1.3.0',
      'REQUEST': 'GetMap',
//                     'LAYERS': layer_name, // US Elevation
      'STYLES': '',
      'BBOX': bbox_mercator,
      'WIDTH': 512,
      'HEIGHT': 512,
      'FORMAT': 'image/png',
      'TRANSPARENT': true,
      'SRS': projection,
      'TILED': true
             // TODO: What if anythin should be in SLD_BODY?
             // 'SLD_BODY': sld
    };

    if (query_params['SLD_BODY']) {
      local_params['SLD_BODY'] = query_params['SLD_BODY'];
    }

    return base_url + '&' + $.param(local_params);
  });

  return layer_name;
};

MapObject.prototype.add_vector_layer = function (name, data, vis_params, query_params) {
  var layer = this.geojsmap.createLayer('feature');
  var start = 0;
  vis_params = vis_params || {};
  JsonReader({layer: layer}).read(data, function (features) {
    var colors = vis_params.colors;
    if (colors) {
      _.each(features, (feature) => {
        var data = feature.data() || [];
        var feature_start = start;
        feature.style('fillColor', (d, i, e, j) => {
          var index = (feature_start + j) % colors.length;
          return colors[index];
        });
        start += data.length;
      });
      layer.draw();
    }
  });
  layer.name(name);
  return name;
};

export default MapObject;
