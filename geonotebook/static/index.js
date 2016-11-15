define(
    ["require",
     "jquery",
     "underscore",
     "base/js/namespace",
     "base/js/events",
     "./lib/jsonrpc",
     "./map"],

    function(require, $, _, Jupyter, events, jsonrpc, Map){

        // the Geonotebook object manages the comm channel that is opened on
        // kernel initialization,  the 'Map' object,  which is a wrapper around
        // a GeoJS map as well as the _remote object for making remote proceedure
        // calls to the Python kernel.
        var Geonotebook = function(){
            this.map = null;
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

        Geonotebook.prototype._remote_class = "geonotebook.kernel.Geonotebook";

        Geonotebook.prototype._unwrap = function(msg){
            return msg.content.data;
        };


        Geonotebook.prototype.handle_comm_msg = function(message){
            var msg = this._unwrap(message)

            if(msg.method == "set_protocol" ){
                // initialize router object
                this.router.set_protocol(msg.data);
            } else {
                try {
                    this.router.recv_msg(msg)
                } catch(ex) {
                    // Should catch jsonRPC errors and handle them
                    // seperately from regular errors
                    //this.router.send_msg(
                    //    jsonrpc.response(null, jsonrpc.InternalError(ex), msg.id));
                    throw ex
                }
            }
        };

        Geonotebook.prototype.handle_kernel = function(Jupyter, kernel) {
            if (kernel.comm_manager) {
                var comm = kernel.comm_manager.new_comm('geonotebook', this.map.get_protocol());
                comm.on_msg(this.handle_comm_msg.bind(this));

                this.router = jsonrpc.router;
                this.router.set_comm(comm);
                // HACK to support object routing
                this.router.geonotebook = this;

            }
        };

        Geonotebook.prototype.register_events = function(Jupyter, events) {
            if (Jupyter.notebook && Jupyter.notebook.kernel) {
                this.handle_kernel(Jupyter, Jupyter.notebook.kernel);
            }

            events.on('kernel_created.Kernel kernel_created.Session kernel_restarted.Kernel', function(event, data) {
                this.handle_kernel(Jupyter, data.kernel);
            }.bind(this));
        };

        Geonotebook.prototype.init_html_and_css = function(){
            $('#ipython-main-app').after('<div id="geonotebook-panel"><div id="geonotebook-map" /></div>');
        };

        Geonotebook.prototype.bind_key_to_geonotebook_event = function(key_binding, action_name, action_opts) {
            var prefix = 'geonotebook';

            action_opts = action_opts || {}
            action_opts.handler = function () {
                this.map.geojsmap.geoTrigger(prefix + ":" + action_name)
            }.bind(this);

            var full_action_name = Jupyter.actions.register(action_opts, action_name, prefix);
            Jupyter.keyboard_manager.command_shortcuts.add_shortcut(key_binding, full_action_name);

            return full_action_name;

        };

        Geonotebook.prototype.load_annotation_buttons = function() {
            point_event = this.bind_key_to_geonotebook_event(
                'g,p', 'point_annotation_mode', {
                    icon: 'fa-circle-o',
                    help    : 'Start a point annotation',
                    help_index : 'zz',

                });
            rect_event  = this.bind_key_to_geonotebook_event(
                'g,r', 'rectangle_annotation_mode', {
                    icon: 'fa-square-o',
                    help    : 'Start a rectangle annotation',
                    help_index : 'zz',
                });

            poly_event  = this.bind_key_to_geonotebook_event(
                'g,g', 'polygon_annotation_mode', {
                    icon: 'fa-lemon-o',
                    help    : 'Start a polygon annotation',
                    help_index : 'zz',
                });

            Jupyter.toolbar.add_buttons_group([point_event, rect_event, poly_event]);

        };

        Geonotebook.prototype.load_ipython_extension = function(){
            if (Jupyter.kernelselector.current_selection == "geonotebook2" ||
                Jupyter.kernelselector.current_selection == "geonotebook3") {
                this.init_html_and_css();
                this.map = new Map(this);
                this.register_events(Jupyter, events);

                this.load_annotation_buttons();
                // Expose globablly for debugging purposes
                Jupyter.map = this.map;
            }
        };

        var geonotebook =  new Geonotebook()
        return geonotebook;

    });
