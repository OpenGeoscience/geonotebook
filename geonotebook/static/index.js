define(
    ["base/js/namespace",
     "base/js/events"],
    function(Jupyter, events){
        var comm;

        function handle_geocomm_msg(msg) {
            console.log(msg['content']['data']);
        }

        function handle_kernel(Jupyter, kernel) {
            if (kernel.comm_manager && kernel.widget_manager === undefined) {
                comm = kernel.comm_manager.new_comm('test', {});
                comm.on_msg(handle_geocomm_msg);

                // Expose this globaly for testing purposes
                Jupyter.geo_comm = comm;

                console.log("HANDLE KERNEL COMMS HERE");
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

        function load_ipython_extension(){
            register_events(Jupyter, events);
            console.log("loaded geonotebook");
        }

        return {
            load_ipython_extension: load_ipython_extension
        };
    });
