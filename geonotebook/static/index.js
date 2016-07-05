define(
    ["require",
     "jquery",
     "base/js/namespace",
     "base/js/events",
     "./map"],

    function(require, $, Jupyter, events, Map){
        var Geonotebook = function(){
            this.comm = null;
            this.map = null;

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

        Geonotebook.prototype.handle_geocomm_msg = function(msg) {
            console.log(msg);
            console.log(msg['content']['data']);
        };

        Geonotebook.prototype.handle_kernel = function(Jupyter, kernel) {
            if (kernel.comm_manager) {
                this.comm = kernel.comm_manager.new_comm('geonotebook', this.map.get_protocol());
                this.comm.on_msg(this.handle_geocomm_msg);

                // Expose this globaly for testing purposes
                Jupyter.geo_comm = this.comm;
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
