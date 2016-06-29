define(
    ["require",
     "base/js/namespace",
     "base/js/events",
     "./lib/geo"],

    function(require, Jupyter, events, geo){
        var comm;
        var map;

        function handle_geocomm_msg(msg) {
            console.log(msg['content']['data']);
        }

        function handle_kernel(Jupyter, kernel) {
            if (kernel.comm_manager) {
                comm = kernel.comm_manager.new_comm('test', {});
                comm.on_msg(handle_geocomm_msg);

                // Expose this globaly for testing purposes
                Jupyter.geo_comm = comm;
            }
        }


        function register_events(Jupyter, events) {
            if (Jupyter.notebook && Jupyter.notebook.kernel) {
                handle_kernel(Jupyter, Jupyter.notebook.kernel);
            }

            events.on('kernel_created.Kernel kernel_created.Session', function(event, data) {
                handle_kernel(Jupyter, data.kernel);
            });
        }

        function add_map_dom(){
            $('head').append(
                $("<link/>")
                    .attr("href", require.toUrl('./css/styles.css'))
                    .attr("rel", "stylesheet")
                    .attr("type", "text/css")
            );
            $('#ipython-main-app').after("<div id='geonotebook_panel'><div id='geonotebook-map' /></div>");

            map = geo.map({node: '#geonotebook-map',
                           width: $("#geonotebook-map").width(),
                           height: $("#geonotebook-map").height()
                          });
            map.createLayer('osm');

            // Expose this globally for testing purposes
            Jupyter.map = map;

        }

        function load_ipython_extension(){
            register_events(Jupyter, events);

            add_map_dom();
            console.log("loaded geonotebook");
        }

        return {
            load_ipython_extension: load_ipython_extension
        };
    });
