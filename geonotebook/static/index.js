define(
    ["require",
     "jquery",
     "underscore",
     "base/js/namespace",
     "base/js/events",
     "./lib/jsonrpc",
     "./map"],

    function(require, $, _, Jupyter, events, jsonrpc, Map){

        var Remote = function(notebook, protocols){
            this.notebook = notebook;

            _.each(protocols, function(protocol){
                this[protocol.procedure] = function(){
                    var params = Array.from(arguments);
                    // how to handle kwargs?
                    var msg = jsonrpc.request(protocol.procedure, params);
                    this.notebook.send_msg(msg);

                    return msg;

                }.bind(this);

            }, this);
        };

        var Geonotebook = function(){
            this.comm = null;
            this.map = null;
            this.protocol_negotiation_complete = false;
            this._remote = null;
            this._callbacks = {};
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

        Geonotebook.prototype.recv_msg = function(msg) {
            var rpc_msg = this._unwrap(msg);

            // TODO: move this into request/response like a
            //       normal method.
            if(rpc_msg.method == "set_protocol" &&
               this.protocol_negotiation_complete === false){
                // set up remote object
                this._remote = new Remote(this, rpc_msg.data);
                this.protocol_negotiation_complete = true;
            } else if(this.protocol_negotiation_complete) {

                // Handle a response
                if( jsonrpc.is_response(rpc_msg) ){
                    if( rpc_msg.id in this._callbacks ){
                        // Resolve the callback
                        this._callbacks[rpc_msg.id]( rpc_msg );
                    } else {
                        // Warning - couldn't find callback
                    }
                }
                // Handle a request
                else if( jsonrpc.is_request(rpc_msg) ) {
                    try {
                        var result = this.map[rpc_msg.method].apply(this.map, rpc_msg.params);
                        this.send_msg(jsonrpc.response(result, null, rpc_msg.id));
                    } catch (ex) {
                        this.send_msg(jsonrpc.response(null, ex, rpc_msg.id));
                        console.log(ex);
                    }
                } else {
                    // Error - could not parse a message
                }

            } else {
                // log an error
                console.log("ERROR: Recieved a " + rpc_msg.method + " message " +
                            "but protocol negotiation is not complete.");
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


        Geonotebook.prototype.load_ipython_extension = function(){
            this.map = new Map(this, '#ipython-main-app');
            this.register_events(Jupyter, events);


            // Expose globablly for debugging purposes
            Jupyter.map = this.map;

            console.log("loaded geonotebook");
        };

        return new Geonotebook();
    });
