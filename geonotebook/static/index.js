define(
    ["require",
     "jquery",
     "underscore",
     "base/js/namespace",
     "base/js/events",
     "./map"],

    function(require, $, _, Jupyter, events, Map){
        var json_rpc_request = function(method, params, opts){
            opts = _.defaults((typeof opts === 'undefined') ? {} : opts,
                              {jsonrpc: "2.0"});

            return _.extend({
                method: method,
                params: params,
                id: "TESTID"}, opts);
        };


        var Remote = function(notebook, protocols){
            this.notebook = notebook;

            _.each(protocols, function(protocol){
                this[protocol.procedure] = function(){
                    var params = Array.from(arguments);
                    // how to handle kwargs?
                    this.notebook.send_msg(
                        json_rpc_request(protocol.procedure, params));

                }.bind(this);

            }, this);
        };

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

        Geonotebook.prototype.recv_msg = function(msg) {
            var rpc_msg = this._unwrap(msg);

            if(rpc_msg.method == "set_protocol" &&
               this.protocol_negotiation_complete === false){
                // set up remote object
                this._remote = new Remote(this, rpc_msg.data);
                this.protocol_negotiation_complete = true;
            } else if(this.protocol_negotiation_complete) {
                // handle a message

                // Validate message

                this.map[rpc_msg.method].apply(this.map, rpc_msg.params);
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
