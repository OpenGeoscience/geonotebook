import _ from 'underscore';

import * as constants from './constants';
import request from './request';
import ReplyCallback from './ReplyCallback';

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
        throw constants.InvalidRequest(
          'Too few arguments passed to ' + protocol.procedure);
      } else if (args.length > protocol.required.length + 1) {
        throw constants.InvalidRequest(
          'Too many arguments passed to ' + protocol.procedure);
        // Options have been passed in (maybe)
      } else if (args.length === protocol.required.length + 1) {
        optionals = args.pop();
        // optionals is not an object?
        if (optionals === null || !_.isObject(optionals)) {
          throw constants.InvalidRequest(
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
      var msg = request(protocol.procedure, params);
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

export default Remote;
