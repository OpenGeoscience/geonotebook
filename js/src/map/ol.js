import Attribution from 'ol/attribution';
import Collection from 'ol/collection';
import Map from 'ol/map';
import proj from 'ol/proj';
import View from 'ol/view';

import condition from 'ol/events/condition';

import GeoJSON from 'ol/format/geojson';

import interaction from 'ol/interaction';
import Draw from 'ol/interaction/draw';

import VectorLayer from 'ol/layer/vector';
import TileLayer from 'ol/layer/tile';

import VectorSource from 'ol/source/vector';
import XYZ from 'ol/source/xyz';
import TileWMS from 'ol/source/tilewms';

import Circle from 'ol/style/circle';
import Fill from 'ol/style/fill';
import Stroke from 'ol/style/stroke';
import Style from 'ol/style/style';

class OlMap {
  constructor (node) {
    this.olmap = new Map({
      target: node,
      view: new View({
        center: [0, 0],
        zoom: 2
      }),
      interactions: interaction.defaults({doubleClickZoom: false})
    });
    this._annotations = new Collection();
    this._overlay = null;
    this._format = new GeoJSON({
      featureProjection: this.olmap.getView().getProjection(),
      defaultDataProjection: 'EPSG:4326'
    });
  }

  resize (size) {
    this.olmap.setSize([size.width, size.height]);
  }

  set_center (x, y, z) {
    var view = this.olmap.getView();
    view.setCenter(
      proj.fromLonLat([x, y], view.getProjection())
    );
    view.setZoom(z);

    return [x, y, z];
  }

  add_annotation_layer () {
    this._overlay = new VectorLayer({
      source: new VectorSource({features: this._annotations}),
      style: (feature) => this._style_feature(feature),
      opacity: 0.8
    });
    this._overlay.setMap(this.olmap);
    this._annotations.on('add', (evt) => this._annotation_handler(evt));
  }

  add_osm_layer (name, url, vis, query) {
    this._baseLayer = this.olmap.addLayer(new TileLayer({
      source: new XYZ({
        url: url.replace('{s}', 'a'),
        attributions: new Attribution({
          html: vis.attribution || ''
        })
      })
    }));

    return this._baseLayer;
  }

  add_tiled_layer (name, url, vis, query) {
    var params = '';
    if ($.param(query)) {
      params = '?' + $.param(query);
    }
    this._baseLayer = this.olmap.addLayer(new TileLayer({
      source: new XYZ({
        url: `${url}/{x}/{y}/{z}.png?${params}`,
        attributions: new Attribution({
          html: vis.attribution || ''
        })
      })
    }));

    return this._baseLayer;
  }

  add_wms_layer (name, url, vis, query) {
    // TODO: Add SLD parameters
    var layer = new TileLayer({
      source: new TileWMS({
        url: url,
        params: {
          TILED: true
        }
      })
    });

    this.olmap.addLayer(layer);
    return layer;
  }

  add_vector_layer (name, data, vis, query) {
    var colors = (vis || {}).colors || ['#b0de5c'];
    var stroke = new Stroke({
      color: 'black',
      width: 2
    });

    var layer = new VectorLayer({
      source: new VectorSource({
        features: this._format.readFeatures(data)
      }),
      style: (feature) => {
        var index = feature.getProperties()._geonotebook_feature_id % colors.length;
        var color = colors[index];
        var fill = new Fill({
          color
        });
        return new Style({
          fill,
          stroke,
          image: new Circle({
            fill,
            stroke,
            radius: 8
          })
        });
      },
      opacity: 0.8
    });
    this.olmap.addLayer(layer);
    return layer;
  }

  remove_layer (name, layer) {
    this.olmap.removeLayer(layer);
  }

  add_annotation (type, geojson) {
    const feature = this._format.readFeatureFromObject(
      geojson,
      {featureProjection: 'EPSG:3857', dataProjection: 'EPSG:4326'}
    );
    const ignore = this._ignoreEvent;
    // TODO: set id?
    //
    this._ignoreEvent = true;
    this._annotations.push(feature);
    this._ignoreEvent = ignore;
  }

  clear_annotations () {
    this._annotations.clear();
  }

  _annotation_handler (evt) {
    if (this._ignoreEvent) {
      return;
    }

    var feature = evt.element;
    var properties = feature.getProperties() || {};
    var json = this._format.writeFeatureObject(feature);
    var coordinates = json.geometry.coordinates;

    // TODO: set id?

    if (!properties.name) {
      properties.name = json.geometry.type + ' ' + feature.getId();
      feature.setProperties(properties);
    }

    if (json.geometry.type === 'Polygon') {
      coordinates = coordinates[0];
    }

    var meta = {
      id: feature.getId(),
      name: properties.name,
      rgb: properties.rgb
    };

    // TODO: move to mapobject
    this.notebook._remote.add_annotation_from_client(
      this._drawType,
      coordinates,
      meta
    ).then(
      function () {
        console.log('annotation added');
      }, this.rpc_error.bind(this)
    );
  }

  _style_feature (feature) {
    var color = feature.getProperties().rgb;
    if (!color) {
      color = this.next_color();
      feature.setProperties({rgb: color});
    }

    var fill = new Fill({
      color
    });

    var stroke = new Stroke({
      color: 'black',
      width: 2
    });

    return new Style({
      fill,
      stroke,
      image: new Circle({
        fill,
        stroke,
        radius: 8
      })
    });
  }

  trigger_draw (action) {
    if (this._draw) {
      this.olmap.removeInteraction(this._draw);
    }
    if (action === 'point_annotation_mode') {
      this._draw = new Draw({
        features: this._annotations,
        type: 'Point'
      });
      this._drawType = 'point';
    } else if (action === 'rectangle_annotation_mode') {
      this._draw = new Draw({
        features: this._annotations,
        type: 'Circle',
        geometryFunction: Draw.createBox(),
        freehandCondition: condition.noModifierKeys
      });
      this._drawType = 'rectangle';
    } else if (action === 'polygon_annotation_mode') {
      this._draw = new Draw({
        features: this._annotations,
        type: 'Polygon'
      });
      this._drawType = 'polygon';
    } else {
      throw new Error('Unknown annotation mode');
    }

    this._draw.once('drawend', () => {
      this.olmap.removeInteraction(this._draw);
    });
    this.olmap.addInteraction(this._draw);
  }
}

export default OlMap;
