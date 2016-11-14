import './css/styles.css';
import _ from 'underscore';

import * as jsonrpc from './jsonrpc';
import GeoMap from './map';

// This class stores a JSONRPC message and callbacks which are evaluated
// once the Remote object recieves a 'resolve' call with the message's id.
// This is initialized with a JSONRPC message and a function that takes a
// message and sends it across some transport mechanism (e.g. Websocket).
var ReplyCallback = function (msg, send_message) {
  this.state = 'CREATED';
  this.msg = msg;
  this.send_message = send_message;
};

ReplyCallback.prototype.then = function (reply_handler, error_handler) {
  this.reply_handler = reply_handler;
  this.error_handler = error_handler;

  this.send_message(this.msg);
  this.state = 'PENDING';
};

// This takes a list of protocol definitions and dynamically generates methods on
// the object that reflect that protocol.  These methods wrap ReplyCallback
// objects which manage the reply and error callbacks of a remote proceedure call.
// Remote defines a '_callbacks' variable which is a dict of message id's to
// ReplyCallback objects.
var Remote = function (transport, protocols) {
  this.send_msg = transport;
  this._callbacks = {};

  _.each(protocols, function (protocol) {
    this[protocol.procedure] = function (...args) {
      var optionals = {};
      // too few arguments
      if (args.length < protocol.required.length) {
        throw jsonrpc.InvalidRequest(
          'Too few arguments passed to ' + protocol.procedure);
      } else if (args.length > protocol.required.length + 1) {
        throw jsonrpc.InvalidRequest(
          'Too many arguments passed to ' + protocol.procedure);
        // Options have been passed in (maybe)
      } else if (args.length === protocol.required.length + 1) {
        optionals = args.pop();
        // optionals is not an object?
        if (optionals === null || !_.isObject(optionals)) {
          throw jsonrpc.InvalidRequest(
            'Optional arguments must be an object, recieved ' +
              optionals + ' for proceedure ' + protocol.proceedure);
        }
      } // else args.length == required.length and optionals should be empty

      var params = _.zip(args, protocol.required).map(function ([a, p]) {
        return {key: p.key, value: a, required: true};
      }).concat(_.keys(optionals).map(function (k) {
        return {key: k, value: optionals[k], required: false};
      }));
      // how to handle kwargs?
      var msg = jsonrpc.request(protocol.procedure, params);
      // Generating a UUID http://stackoverflow.com/a/2117523
      msg.id = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        var r = Math.random() * 16 | 0;
        var v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
      });

      this._callbacks[msg.id] = new ReplyCallback(msg, this.send_msg);

      return this._callbacks[msg.id];
    }.bind(this);
  }, this);
};

Remote.prototype.resolve = function (msg) {
  if (msg.id in this._callbacks) {
    // Resolve the callback
    if (msg.error !== null) {
      this._callbacks[msg.id].error_handler(msg.error);
    } else {
      this._callbacks[msg.id].reply_handler(msg.result);
    }

    delete this._callbacks[msg.id];
  } else {
    console.log("WARNING: Couldn't find callback for message id: " + msg.id); // eslint-disable-line no-console
  }
};

// the Geonotebook object manages the comm channel that is opened on
// kernel initialization,  the 'Map' object,  which is a wrapper around
// a GeoJS map as well as the _remote object for making remote proceedure
// calls to the Python kernel.
var Geonotebook = function (Jupyter, events) {
  this.comm = null;
  this.map = null;
  this.protocol_negotiation_complete = false;
  this._remote = null;

  this.init_html_and_css();
  this.map = new GeoMap(this);
  this.register_events(Jupyter, events);
  this.load_annotation_buttons(Jupyter);
  Jupyter.map = this.map;
};

Geonotebook.prototype._unwrap = function (msg) {
  return msg.content.data;
};

Geonotebook.prototype.send_msg = function (msg) {
  this.comm.send(msg);
};

Geonotebook.prototype.get_object = function (msg) {
  // TODO: Add object routing here
  return this.map;
};

// Here we resolve the passed in parameters availale in msg.params
// with the arguments of the function defined by fn.$arg_meta.
// fn.$arg_meta is an array of objects like the following:
//     [{key: 'layer_name', default: false},
//      {key: 'url', default: false},
//      (key: 'opacity', default2: 1.0}]
// while msg.params is a list like the following:
//     [{key: 'layer_name', value: 'foobar', required: true},
//       {key: 'url', value: 'http://example.com/x/y/z.png',
//        required: true}]
//
// notice in this example msg.params does not have 'opacity.' That
// is ok because opacity is an 'optional' argument, in this case
// resolve_arg_list will return undefined for opacity and the default
// argument defined on the function will take over.
Geonotebook.prototype.resolve_arg_list = function (fn, msg) {
  if (fn.$arg_meta !== undefined) {
    // make a hash of the parameters where param['key'] => param
    var param_hash = msg.params.reduce(function (obj, p) {
      obj[p['key']] = p;
      return obj;
    }, {});

    return fn.$arg_meta.map(function (arg) {
      // we found the parameter in the param_hash
      if (param_hash[arg['key']] !== undefined) {
        return param_hash[arg['key']]['value'];
      } else if (arg['default']) {
        return undefined;
      } else {
        throw jsonrpc.InvalidParam(
          msg.method + ' did not recieve a required param ' + arg['key']);
      }
    });
  } else {
    throw jsonrpc.ParseError('$arg_meta not available on ' + msg.method + '!');
  }
};

Geonotebook.prototype.recv_msg = function (message) {
  var msg = this._unwrap(message);
  // TODO: move this into request/response like a
  //       normal method.
  if (msg.method === 'set_protocol') {
    // set up remote object
    this._remote = new Remote(this.send_msg.bind(this), msg.data);
    this.protocol_negotiation_complete = true;

    // Once protocol negotiation is complete create the geojs map
    // and add the base OSM layer
    this.map.init_map();
  } else if (this.protocol_negotiation_complete) {
    // Pass response messages on to remote to be resolved
    if (jsonrpc.is_response(msg)) {
      this._remote.resolve(msg);
    } else if (jsonrpc.is_request(msg)) {
      try {
        // Apply the map method from the msg on the parameters
        var obj = this.get_object(msg);

        if (obj[msg.method] !== undefined) {
          var result = obj[msg.method].apply(
            this.map, this.resolve_arg_list(obj[msg.method], msg));
          // Reply with the result of the call
          this.send_msg(jsonrpc.response(result, null, msg.id));
        } else {
          throw jsonrpc.MethodNotfound('Method ' + msg.method + ' not found!');
        }
      } catch (ex) {
        // If we catch an error report it back to the RPC caller
        this.send_msg(jsonrpc.response(null, ex, msg.id));
      }
    } else {
      // Not a response or a request - send parse error
      this.send_msg(
        jsonrpc.response(null, jsonrpc.ParseError('Could not parse message'), msg.id));
    }
  } else {
    // Protocol negotiation not complete - send internal error
    this.send_msg(
      null, jsonrpc.InternalError('ERROR: Recieved a ' + msg.method + ' message ' +
        'but protocol negotiation is not complete.'), msg.id);
  }
};

Geonotebook.prototype.handle_kernel = function (Jupyter, kernel) {
  if (kernel.comm_manager) {
    this.comm = kernel.comm_manager.new_comm('geonotebook', this.map.get_protocol());

    this.comm.on_msg(this.recv_msg.bind(this));
  }
};

Geonotebook.prototype.register_events = function (Jupyter, events) {
  if (Jupyter.notebook && Jupyter.notebook.kernel) {
    this.handle_kernel(Jupyter, Jupyter.notebook.kernel);
  }

  events.on('kernel_created.Kernel kernel_created.Session kernel_restarted.Kernel', function (event, data) {
    this.handle_kernel(Jupyter, data.kernel);
  }.bind(this));
};

Geonotebook.prototype.init_html_and_css = function () {
  $('#ipython-main-app').after('<div id="geonotebook-panel"><div id="geonotebook-map" /></div>');
};

Geonotebook.prototype.bind_key_to_geonotebook_event = function (Jupyter, key_binding, action_name, action_opts) {
  var prefix = 'geonotebook';

  action_opts = action_opts || {};
  action_opts.handler = function () {
    this.map.geojsmap.geoTrigger(prefix + ':' + action_name);
  }.bind(this);

  var full_action_name = Jupyter.actions.register(action_opts, action_name, prefix);
  Jupyter.keyboard_manager.command_shortcuts.add_shortcut(key_binding, full_action_name);

  return full_action_name;
};

Geonotebook.prototype.load_annotation_buttons = function (Jupyter) {
  var point_event = this.bind_key_to_geonotebook_event(
    Jupyter,
    'g,p', 'point_annotation_mode', {
      icon: 'fa-circle-o',
      help: 'Start a point annotation',
      help_index: 'zz'

    });
  var rect_event = this.bind_key_to_geonotebook_event(
    Jupyter,
    'g,r', 'rectangle_annotation_mode', {
      icon: 'fa-square-o',
      help: 'Start a rectangle annotation',
      help_index: 'zz'
    });

  var poly_event = this.bind_key_to_geonotebook_event(
    Jupyter,
    'g,g', 'polygon_annotation_mode', {
      icon: 'fa-lemon-o',
      help: 'Start a polygon annotation',
      help_index: 'zz'
    });

  Jupyter.toolbar.add_buttons_group([point_event, rect_event, poly_event]);
};

export default Geonotebook;
