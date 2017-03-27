import _ from 'underscore';
import 'geojs';

import GeoMap from 'geojs/map';
import JsonReader from 'geojs/jsonReader';
import event from 'geojs/event';
import { pointAnnotation, rectangleAnnotation, polygonAnnotation } from 'geojs/annotation';

import BaseMap from './base';

const geo_event = event;

class GeoJSMap extends BaseMap {
  _init_map () {
    this.geojsmap = GeoMap({
      node: this.node,
      allowRotation: false
    });
  }

  _resize (size) {
    this.geojsmap.size(size);
  }

  _set_center (x, y, z) {
    this.geojsmap.center({x, y});
    this.geojsmap.zoom(z);
    return [x, y, z];
  }

  _add_annotation_layer (name) {
    var layer = this.geojsmap.createLayer('annotation', {
      annotations: ['rectangle', 'point', 'polygon']
    });
    layer.name(name);

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
    return layer;
  }

  _add_osm_layer (name, url, vis, query) {
    var opts = {};
    if (vis.attribution) {
      opts.attribution = vis.attribution;
    }
    var osm = this.geojsmap.createLayer('osm', opts);

    osm.name(name);
    osm.url(url);

      // make sure zindex is explicitly set
    this._set_layer_zindex(osm, vis['zIndex']);

    return osm;
  }

  _add_tiled_layer (name, url, vis, query) {
    var layer = this.geojsmap.createLayer('osm', {
      attribution: null,
      keepLower: false
    });
    var params = '';

    if ($.param(query)) {
      params = '?' + $.param(query);
    }

    layer.name(name);
    layer.url((x, y, z) => `${url}/${x}/${y}/${z}.png${params}`);

      // make sure zindex is explicitly set
    this._set_layer_zindex(layer, vis['zIndex']);

    return layer;
  }

  _add_wms_layer (name, url, vis, query) {
    var projection = query['projection'] || 'EPSG:3857';

    var wms = this.geojsmap.createLayer('osm', {
      keepLower: false,
      attribution: null
    });

      // make sure zindex is explicitly set
    this._set_layer_zindex(wms, query['zIndex']);

    wms.name(name);

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
        'STYLES': '',
        'BBOX': bbox_mercator,
        'WIDTH': 512,
        'HEIGHT': 512,
        'FORMAT': 'image/png',
        'TRANSPARENT': true,
        'SRS': projection,
        'TILED': true
      };

      if (query['SLD_BODY']) {
        local_params['SLD_BODY'] = query['SLD_BODY'];
      }

      return url + '&' + $.param(local_params);
    });

    return wms;
  }

  _add_vector_layer (name, url, vis, query) {
    var data = url;
    var layer = this.geojsmap.createLayer('feature');
    vis = vis || {};

    // make sure zindex is explicitly set
    this._set_layer_zindex(layer, vis['zIndex']);

    var start = 0;
    JsonReader({layer}).read(data, function (features) {
      var colors = vis.colors;
      if (colors) {
        _.each(features, (feature) => {
          var data = feature.data() || [];
          var feature_start = start;
          feature.style('fillColor', (d, i, e, j) => {
            // point and polygon features have different interfaces, so make
            // changes to the arguments to unify the rest of the styling function.
            if (e) {
              d = e;
              i = j;
            }

            // we are going to extremes to avoid throwing errors
            var properties = d.properties || {};
            var id = properties._geonotebook_feature_id;
            if (id === undefined) {
              id = feature_start + i;
            }
            var index = id % colors.length;
            return colors[index];
          });
          start += data.length;
        });
      }
      layer.draw();
    });
    layer.name(name);
    return layer;
  }

  _remove_layer (name, layer) {
    this.geojsmap.deleteLayer(layer);
  }

  _add_annotation (type, geojson) {
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
    var annotation_layer = this.get_layer('annotation');
    var annotation;
    function _handler (evt) {
      annotation = evt.annotation;
    }
    annotation_layer.geoOn(geo_event.annotation.add, _handler);
    const coordinates = geojson.geometry.coordinates;
    const style = geojson.properties;
    _.defaults(style, {
      fillColor: style.rgb,
      fillOpacity: 0.8,
      lineWidth: 2
    });

    if (type === 'point') {
      annotation_layer.addAnnotation(pointAnnotation({
        position: {
          x: coordinates[0],
          y: coordinates[1]
        },
        style
      }));
    } else if (type === 'rectangle') {
      annotation_layer.addAnnotation(rectangleAnnotation({
        corners: _.map(coordinates[0], (coords) => {
          return {
            x: coords[0],
            y: coords[1]
          };
        }),
        style
      }));
    } else if (type === 'polygon') {
      annotation_layer.addAnnotation(polygonAnnotation({
        vertices: _.map(coordinates[0], (coords) => {
          return {
            x: coords[0],
            y: coords[1]
          };
        }),
        style
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

    if (style.name) {
      annotation.name(style.name);
    }
  }

  _clear_annotations () {
    var annotation_layer = this.get_layer('annotation');
    return annotation_layer.removeAllAnnotations();
  }

  state_annotation_handler (evt) {
    var annotation = evt.annotation;
    if (_.contains(['point', 'polygon', 'rectangle'], annotation.type())) {
      this._add_annotation_handler(annotation);
    }
  }

  _get_layer (name) {
    return _.find(this.geojsmap.layers(),
                    function (l) { return l.name() === name; });
  }

  _trigger_draw (action) {
    this.geojsmap.geoTrigger('geonotebook:' + action);
  }

  _set_layer_zindex (layer, index) {
    if (index !== undefined) {
      var annotation_layer = this.get_layer('annotation');
      layer.zIndex(index);
      if (annotation_layer !== null) {
              // Annotation layer should always be on top
        var max = _.max(_.invoke(this.geojsmap.layers(), 'zIndex'));
        annotation_layer.zIndex(max + 1);
      }
    }
  }

  _map_coordinates (coordinates, type) {
    if (type === 'point') {
      return [coordinates[0].x, coordinates[0].y];
    }
    return _.map(coordinates, (c) => {
      return [c.x, c.y];
    });
  }

  _add_annotation_handler (annotation) {
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
    this.on_add_annotation(annotation.type(), coordinates, annotation_meta);
  }
}

export default GeoJSMap;
