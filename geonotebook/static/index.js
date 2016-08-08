define(
    ["require",
     "jquery",
     "underscore",
     "base/js/namespace",
     "base/js/events",
     "./lib/jsonrpc",
     "./map"],

    function(require, $, _, Jupyter, events, jsonrpc, Map){

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
        var Remote = function(transport, protocols){
            this.send_msg = transport;
            this._callbacks = {};

            _.each(protocols, function(protocol){
                this[protocol.procedure] = function(){
                    var params = Array.from(arguments);
                    // how to handle kwargs?
                    var msg = jsonrpc.request(protocol.procedure, params);

                    this._callbacks[msg.id] = new ReplyCallback(msg, this.send_msg);

                    return this._callbacks[msg.id];

                }.bind(this);

            }, this);
        };

        Remote.prototype.resolve = function(msg){
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

        // the Geonotebook object manages the comm channel that is opened on
        // kernel initialization,  the 'Map' object,  which is a wrapper around
        // a GeoJS map as well as the _remote object for making remote proceedure
        // calls to the Python kernel.
        var Geonotebook = function(){
            this.comm = null;
            this.map = null;
            this.protocol_negotiation_complete = false;
            this._remote = null;
            // Expose the geonotebook object on the Jupyter object
            // This makes the notebook available from the
            // base/js/namespace AMD
            var that = this;
            if(!Jupyter.hasOwnProperty('Geonotebook')){
                Object.defineProperty(Jupyter, 'Geonotebook', {
                    get: function(){
                        return that;
                    },
                    enumerable: true,
                    configurable: false
                });
            }
        };

        Geonotebook.prototype._unwrap = function(msg){
            return msg.content.data;
        };

        Geonotebook.prototype.send_msg = function(msg) {
            this.comm.send(msg);
        };

        Geonotebook.prototype.recv_msg = function(message) {
            var msg = this._unwrap(message);

            // TODO: move this into request/response like a
            //       normal method.
            if(msg.method == "set_protocol" &&
               this.protocol_negotiation_complete === false){
                // set up remote object
                this._remote = new Remote(this.send_msg.bind(this), msg.data);
                this.protocol_negotiation_complete = true;

                // Once protocol negotiation is complete create the geojs map
                // and add the base OSM layer
                this.map.init_map();
            } else if(this.protocol_negotiation_complete) {

                // Pass response messages on to remote to be resolved
                if( jsonrpc.is_response(msg) ){
                    this._remote.resolve(msg);
                }

                // Handle a RPC request
                else if( jsonrpc.is_request(msg) ) {
                    try {
                        // Apply the map method from the msg on the paramaters
                        var result = this.map[msg.method].apply(this.map, msg.params);

                        // Reply with the result of the call
                        this.send_msg(jsonrpc.response(result, null, msg.id));
                    } catch (ex) {
                        // If we catch an error report it back to the RPC caller
                        this.send_msg(jsonrpc.response(null, ex, msg.id));
                    }
                } else {
                    // Not a response or a request - send parse error
                    this.send_msg(
                        jsonrpc.response(null, jsonrpc.ParseError("Could not parse message"), msg.id));
                }

            } else {
                // Protocol negotiation not complete - send internal error
                this.send_msg(
                    null, jsonrpc.InternalError("ERROR: Recieved a " + msg.method + " message " +
                                                "but protocol negotiation is not complete."), msg.id);
            }
        };

        Geonotebook.prototype.handle_kernel = function(Jupyter, kernel) {
            if (kernel.comm_manager) {
                this.comm = kernel.comm_manager.new_comm('geonotebook', this.map.get_protocol());

                this.comm.on_msg(this.recv_msg.bind(this));

            }
        };

        Geonotebook.prototype.register_events = function(Jupyter, events) {
            if (Jupyter.notebook && Jupyter.notebook.kernel) {
                this.handle_kernel(Jupyter, Jupyter.notebook.kernel);
            }

            events.on('kernel_created.Kernel kernel_created.Session', function(event, data) {
                this.handle_kernel(Jupyter, data.kernel);
            });
        };


        Geonotebook.prototype.init_html_and_css = function(){
            $('head').append(
                $('<link/>')
                    .attr('href', require.toUrl('./css/styles.css'))
                    .attr('rel', 'stylesheet')
                    .attr('type', 'text/css')
            );
            $('#ipython-main-app').after('<div id="geonotebook_panel"><div id="geonotebook-map" /></div>');

        };

        Geonotebook.prototype.load_ipython_extension = function(){
            this.map = new Map(this);
            this.register_events(Jupyter, events);

            this.init_html_and_css();




            // Expose globablly for debugging purposes
            Jupyter.map = this.map;
            console.log("DEBUG: loaded geonotebook");

        };

        return new Geonotebook();
    });
