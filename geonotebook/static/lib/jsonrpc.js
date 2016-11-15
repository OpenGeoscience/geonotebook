define(
    ['underscore',
     'base/js/events'
    ],
    function(_, events){
        var JSONRPCError = function(code){
            return function(message, data){

                console.log("JSONRPCError (" +code  + "): " + message);

                if (data !== undefined ){
                    return {
                        code: code,
                        message: message,
                        data: data
                    };
                } else {
                    return {
                        code: code,
                        message: message
                    };
                }
            };
        };

        var ParseError = JSONRPCError(-32700);
        var InvalidRequest = JSONRPCError(-32600);
        var MethodNotFound = JSONRPCError(-32601);
        var InvalidParams = JSONRPCError(-32602);
        var InternalError = JSONRPCError(-32603);
        var ServerError = JSONRPCError(-32000);


        function request(method, params, opts){
            opts = _.defaults((typeof opts === 'undefined') ? {} : opts,
                              {jsonrpc: "2.0"});

            return _.extend({
                method: method,
                params: params}, opts);
        }
        function response(result, error, id){
            // TODO validate taht result/error are mutually exclusive
            return {result: result,
                    error: error,
                    id: id };
        }

        function is_request(msg){
                return 'method' in msg && 'params' in msg && 'id' in msg;
        }
        function is_response(msg){
                return 'result' in msg && 'error' in msg && 'id' in msg;
        }


        // This class stores a JSONRPC message and callbacks which are evaluated
        // once the Remote object recieves a 'resolve' call with the message's id.
        // This is initialized with a JSONRPC message and a function that takes a
        // message and sends it across some transport mechanism (e.g. Websocket).
        var ReplyCallback = function(msg, send_message) {
            this.state = "CREATED";
            this.msg = msg;
            this.send_message = send_message;
        };

        ReplyCallback.prototype.then = function(reply_handler, error_handler){
            this.reply_handler = reply_handler;
            this.error_handler = error_handler;

            this.send_message(this.msg);
            this.state = "PENDING";
        };

        // This takes a list of protocol definitions and dynamically generates methods on
        // the object that reflect that protocol.  These methods wrap ReplyCallback
        // objects which manage the reply and error callbacks of a remote proceedure call.
        // Remote defines a '_callbacks' variable which is a dict of message id's to
        // ReplyCallback objects.
        var Remote = function(transport,  add_promise, protocols){
            this.send_msg = transport;
            this.add_promise = add_promise;
            this._callbacks = {};

            _.each(protocols, function(protocol){

                this[protocol.procedure] = function(...args){
                    var optionals = {}
                    // too few arguments
                    if(args.length < protocol.required.length){
                        throw InvalidRequest(
                            "Too few arguments passed to " + protocol.procedure);

                    } else if (args.length > protocol.required.length + 1) {
                        throw InvalidRequest(
                            "Too many arguments passed to " + protocol.procedure);
                    // Options have been passed in (maybe)
                    } else if (args.length == protocol.required.length + 1) {
                        optionals = args.pop();
                        // optionals is not an object?
                        if(optionals === null || typeof optionals !== 'object'){
                            throw InvalidRequest(
                                "Optional arguments must be an object, recieved " +
                                    optionals + " for proceedure " + protocol.proceedure);

                        }
                    } // else args.length == required.length and optionals should be empty

                    var params = _.zip(args, protocol.required).map(function([a, p]){
                        return {key: p.key, value: a, required: true};
                    }).concat(_.keys(optionals).map(function(k){
                        return {key: k, value: optionals[k], required: false};
                    }));

                    // how to handle kwargs?
                    var msg = request(protocol.procedure, params);
                    // Generating a UUID http://stackoverflow.com/a/2117523
                    msg.id = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
                        var r = Math.random()*16|0, v = c == 'x' ? r : (r&0x3|0x8);
                        return v.toString(16);
                    });

                    return this.add_promise(msg);

                }.bind(this);

            }, this);
        };


        var Router = function(){
            this._callbacks = {}
            this._class_mapping = {};

            this.comm = null;
            this.remote_protocol = null;
            this.protocol_negotiation_complete = false;
        };

        Router.prototype.register_class = function(cls, remote_cls){
            this._class_mapping[cls.name] = cls;
            cls.prototype.remote_class = remote_cls;
        };

        Router.prototype.remote_factory = function(obj){
            if( obj.remote_class !== undefined){
                if(this.remote_protocol[obj.remote_class] !== undefined ){
                    return new Remote(
                        this.send_msg, this.add_promise,
                        this.remote_protocol[obj.remote_class])
                }
            }
            // Return a Remote object with an empty protocol
            return new Remote(this.send_msg, this.add_promise, []);
        };

        Router.prototype.add_promise = function(msg){
            this._callbacks[msg.id] = new ReplyCallback(msg, this.send_msg);
            return this._callbacks[msg.id];
        };

        Router.prototype.resolve = function(msg){
            if( msg.id in this._callbacks ){
                // Resolve the callback
                if (msg.error !== null){
                    this._callbacks[msg.id].error_handler(msg.error);
                } else {
                    this._callbacks[msg.id].reply_handler(msg.result);
                }

                delete this._callbacks[msg.id];

            } else {
                console.log("WARNING: Couldn't find callback for message id: " + msg.id);
            }
        };

        Router.prototype.set_comm = function(comm){
            this.comm = comm;
        };

        Router.prototype.set_protocol = function(protocol){
            this.remote_protocol = protocol
            this.protocol_negotiation_complete = true;
            events.trigger('geonotebook.protocol_negotiation_complete', this);
        };

        Router.prototype.get_object = function(msg){
            // TODO: Add object routing here
            // HACK
            return this.geonotebook.map;
        };

        Router.prototype.send_msg = function(msg) {
            this.comm.send(msg);
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
        Router.prototype.resolve_arg_list = function(fn, msg){
            if( fn.$arg_meta !== undefined ){
                // make a hash of the parameters where param['key'] => param
                var param_hash = msg.params.reduce(function(obj, p) {
                    obj[p['key']] = p;
                    return obj;
                }, {});

                return fn.$arg_meta.map(function(arg){
                    // we found the parameter in the param_hash
                    if( param_hash[arg['key']] !== undefined) {
                        return param_hash[arg['key']]['value'];
                    } else if (!!arg['default']) {
                        return undefined;
                    } else {
                        throw InvalidParams(
                            msg.method + ' did not recieve a required param ' + arg['key']);
                    }
                });

            } else {
                throw ParseError("$arg_meta not available on " + msg.method + "!");
            }
        }

        Router.prototype.recv_msg = function(msg) {
            // TODO: move this into request/response like a
            //       normal method.
            // Once protocol negotiation is complete create the geojs map
            // and add the base OSM layer
            if(this.protocol_negotiation_complete) {

                // Pass response messages on to remote to be resolved
                if( is_response(msg) ){
                    this.resolve(msg);
                }

                // Handle a RPC request
                else if( is_request(msg) ) {
                    // Apply the map method from the msg on the parameters
                    var obj = this.get_object(msg);

                    if (obj[msg.method] !== undefined){
                        var result = obj[msg.method].apply(
                            obj, this.resolve_arg_list(obj[msg.method], msg));
                        // Reply with the result of the call
                        this.send_msg(response(result, null, msg.id));
                    } else {
                        throw MethodNotFound("Method " + msg.method + " not found!")
                    }

                } else {
                    // Not a response or a request - send parse error
                    throw ParseError("Could not parse message");
                }

            } else {
                // Protocol negotiation not complete - send internal error
                throw InternalError("ERROR: Recieved a " + msg.method + " message " +
                                            "but protocol negotiation is not complete.")
            }
        };


        var router = new Router();

        return {
            router: router,
            request: request,
            response: response,
            is_request: is_request,
            is_response: is_response,
            ParseError: ParseError,
            InvalidRequest: InvalidRequest,
            MethodNotFound: MethodNotFound,
            InvalidParams: InvalidParams,
            InternalError: InternalError,
            ServerError: ServerError
        };
    });
