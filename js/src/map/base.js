import _ from 'underscore';

import annotate from '../jsonrpc/annotate';
import * as constants from '../jsonrpc/constants';

/**
 * Get 4 random hex digits for guid generation.
 */

function S4 () {
  return (((1 + Math.random()) * 0x10000) | 0).toString(16).substring(1);
}

/**
 * A list of default colors to use for new annotations.
 */
const color_palette = [
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
var color_counter = 0;

/**
 * A list of methods that are available for the RPC mechanism.
 */
const msg_types = [
  'get_protocol',
  'set_center',
  'debug',
  'add_layer',
  'update_layer',
  'add_annotation_layer',
  'clear_annotations',
  'remove_layer',
  'add_annotation'
];

/**
 * A mapping from annotation type -> geojson geometry.
 */
const annotation_types = {
  point: 'Point',
  rectangle: 'Polygon',
  polygon: 'Polygon'
};

/**
 * The MapObject class is an abstract interface used by the geonotebook
 * kernel to interface with a specific map renderer.  This class handles
 * all RPC communication and data conversion for the map renderers.
 *
 * Map renderers must implement a number of methods which are often
 * direct delegations to a mapping library.  See the implementations
 * in `./maps/*` for concrete examples about implementing these
 * methods.
 *
 *   * _init_map()
 *   * _resize(size)
 *   * _set_center(x, y, z)
 *   * _add_annotation_layer(name)
 *   * _add_osm_layer(name, url, vis, query)
 *   * _add_wms_layer(name, url, vis, query)
 *   * _add_vector_layer(name, data, vis, query)
 *   * _add_tiled_layer(name, data, vis, query)
 *   * _remove_layer(name, layer)
 *   * _add_annotation(type, geojson)
 *   * _clear_annotations()
 *   * _trigger_draw(action)
 *   * _screenshot()
 */
class MapObject {
  /**
   * Create a map object instance.
   * @param {kernel} notebook The global geonotebook object
   * @param {function} MapClass A map renderer constructor
   */
  constructor (notebook) {
    this.notebook = notebook;
    this.region = null;
    this.layers = {};
    this.msg_types = msg_types;
  }

  /**
   * Initialize the map renderer object.
   */
  init_map () {
    this._init_map();
    return true;
  }

  /**
   * Set the map center and zoom.
   * @param {number} x The map longitude
   * @param {number} y The map latitude
   * @param {number} z The map zoom level
   */
  set_center (x, y, z) {
    if (x < -180.0 || x > 180.0 || y < -90.0 || y > 90.0 || z < 0) {
      throw new constants.InvalidParams('Invalid parameters sent to set_center!');
    }
    return this._set_center(x, y, z);
  }

  /**
   * Add a new layer to the map.  The layer type is inferred from
   * the vis_params object.  This will delegate to the map
   * renderer to generate a layer of the appropriate type.
   * This will also store a reference to the created layer
   * for later modification.
   *
   * @param {string} layer_name A unique layer name
   * @param {string|object} vis_url A base url for fetch tiled data
   * @param {object} vis_params Parameters for styling the layer
   * @param {object} query_params Query parameters added to tile requests
   */
  add_layer (layer_name, vis_url, vis_params, query_params) {
    let layer = null;
    const layer_type = vis_params.layer_type;

    this.remove_layer(layer_name);

    if (layer_type === 'annotation') {
      layer = this._add_annotation_layer(layer_name);
    } else if (layer_type === 'wms') {
      layer = this._add_wms_layer(layer_name, vis_url, vis_params, query_params);
    } else if (layer_type === 'osm') {
      layer = this._add_osm_layer(layer_name, vis_url, vis_params, query_params);
    } else if (layer_type === 'vector') {
      layer = this._add_vector_layer(layer_name, vis_url, vis_params, query_params);
    } else {
      layer = this._add_tiled_layer(layer_name, vis_url, vis_params, query_params);
    }

    if (layer) {
      this.layers[layer_name] = layer;
    }
    return layer_name;
  }

  add_annotation_layer (name) {
    this._add_annotation_layer(name);
    return name;
  }

  /**
   * Update a layer with new options.  This currently just removes and
   * re-adds the layer, but in the future it may be optimized with a new
   * call to the map renderer if there are performance issues.
   */
  update_layer (layer_name, vis_url, vis_params, query_params) {
    return this.add_layer(layer_name, vis_url, vis_params, query_params);
  }

  /**
   * Return a layer object given a name.
   *
   * @param {string} layer_name The name of the layer to remove
   */
  get_layer (layer_name) {
    if (_.has(this.layers, layer_name)) {
      return this.layers[layer_name];
    }
    return null;
  }

  /**
   * Remove a layer from the map.
   *
   * @param {string} layer_name The name of the layer to remove
   */
  remove_layer (layer_name) {
    if (_.has(this.layers, layer_name)) {
      this._remove_layer(layer_name, this.layers[layer_name]);
      delete this.layers[layer_name];
    }
    return true;
  }

  /**
   * Add an annotation from a serialization.
   *
   * @param {point|rectangle|polygon} type The annotation type
   * @param {array} args The coordinates of the annotation geometry
   * @param {object} kwargs Optional arguments for naming and styling
   */
  add_annotation (type, args, kwargs) {
    if (!_.has(annotation_types, type)) {
      throw new constants.InvalidParams('Invalid annotation type.');
    }

    let coordinates = args;
    let id = kwargs.id;

    if (type === 'point') {
      coordinates = args[0];
    } else {
      coordinates = [coordinates[0]];
    }

    if (_.isUndefined(id)) {
      id = this.get_id();
    }

    const name = kwargs.name || type + ' ' + id;
    const rgb = kwargs.rgb || this.next_color();
    const properties = _.extend({
      name, rgb
    }, kwargs);

    const geojson = {
      type: 'Feature',
      geometry: {
        type: annotation_types[type],
        coordinates
      },
      properties,
      id
    };

    this._add_annotation(type, geojson);

    return {
      id,
      name,
      rgb
    };
  }

  /**
   * Remove all rendered annotations from the map.
   */
  clear_annotations () {
    this._clear_annotations();
    return true;
  }

  /**
   * Force resize the map after a layout change.  Uses
   * 100% of the containing node.
   */
  resize () {
    const $el = $(this.node);
    const size = {
      width: $el.width(),
      height: $el.height()
    };
    this._resize(size);
    return size;
  }

  /**
   * Get the node that the map renderer is initialized into.
   */
  get node () {
    return document.getElementById('geonotebook-map');
  }

  /*
   * Generate a list of protocol definitions for the white listed functions
   * in msg_types. This will be passed to the Python geonotebook object and
   * will initialize its RPC object so JS map frunctions can be called from
   * the Python environment.
   */
  get_protocol () {
    return _.map(this.msg_types, (msg_type) => {
      var args = annotate(this[msg_type]);

      return {
        procedure: msg_type,
        required: args.filter(function (arg) { return !arg.default; }),
        optional: args.filter(function (arg) { return !!arg.default; })
      };
    });
  }

  /**
   * Respond to an annotation button click by putting the map into
   * "draw mode".  This is passed off to the map renderer which should
   * provide an implementation.  The client should return a promise
   * that resolves when the draw is complete.
   */
  trigger_draw (action) {
    return this._trigger_draw(action);
  }

  /**
   * Take a screenshot of the current map view and return promise
   * that resolves with a data URI of a png image.
   */
  screenshot () {
    return this._screenshot();
  }

  /**
   * Called after an annotation has been successfully generated on
   * the client to propagate the annotation to the server.
   */
  on_add_annotation (type, coordinates, meta) {
    return this.notebook._remote.add_annotation_from_client(
      type, coordinates, meta
    ).then(
      () => {
        this.debug('annotation added');
      }, this.rpc_error.bind(this)
    );
  }

  /**
   * Return the next color from our color palette.
   */
  next_color () {
    color_counter += 1;
    return color_palette[color_counter % color_palette.length];
  }

  /**
   * Return a random guid.
   */
  get_id () {
    return (S4() + S4() + '-' + S4() + '-' + S4() + '-' + S4() + '-' + S4() + S4() + S4());
  }

  rpc_error (error) {
    console.log('JSONRPCError(' + error.code + '): ' + error.message); // eslint-disable-line no-console
  }

  debug (msg) {
    console.log(msg); // eslint-disable-line no-console
  }
}

export default MapObject;
