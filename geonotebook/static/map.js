define(
    ["jquery",
     "underscore",
     "require",
     "./lib/jsonrpc",
     "./lib/geo",
     "./lib/utils"],
    function($, _, require, jsonrpc, geo, utils){
        var Map = function(notebook, div){
            this.notebook = notebook;
            this.geo = geo;
            this.region = null;

            $('head').append(
                $("<link/>")
                    .attr("href", require.toUrl('./css/styles.css'))
                    .attr("rel", "stylesheet")
                    .attr("type", "text/css")
            );
            $(div).after("<div id='geonotebook_panel'><div id='geonotebook-map' /></div>");

            this.geojsmap = geo.map({node: '#geonotebook-map',
                           width: $("#geonotebook-map").width(),
                           height: $("#geonotebook-map").height()
                               });

            this.geojsmap.createLayer('osm');

            this.geojsmap.geoOn('geo_select', this.geo_select.bind(this));

        };

        Map.prototype.set_region = function(ulx, uly, lrx, lry){

            var msg = this.notebook._remote.set_region(ulx, uly, lrx, lry);

            this.notebook._callbacks[msg.id] = function(msg){
                if (msg.error !== null){
                    // TODO better error handling here
                    console.log("JSONRPCError(" + msg.error.code + "): " + msg.error.message);
                } else {
                    this.region = msg.result;
                }
                delete this.notebook._callbacks[msg.id];
            }.bind(this);

        };

        Map.prototype.geo_select = function(event, args){

            var ul = this.geojsmap.displayToGcs(event.display.upperLeft, "EPSG:4326");
            var lr = this.geojsmap.displayToGcs(event.display.lowerRight, "EPSG:4326");

            this.set_region(ul.x, ul.y, lr.x, lr.y);
        };


        Map.prototype.msg_types = ["get_protocol", "set_center", "_debug"];

        Map.prototype._debug = function(msg){
            console.log(msg);
        };

        Map.prototype.get_protocol = function(){
            return this.msg_types.map(function(msg_type){

                var args = utils.annotate(this[msg_type]);

                return {procedure: msg_type,
                        required: args.filter(function(arg){ return !arg.includes("="); }),
                        optional: args.filter(
                            function(arg){ return arg.includes("="); }).map(
                                function(arg) {
                                    return arg.split("=")[0].trim();
                                })
                       };



            }.bind(this));

        };

        Map.prototype.set_center = function(x, y, z){
            if ( x < -180.0 || x > 180.0 || y < -90.0 || y > 90.0) {
                throw new jsonrpc.InvalidParams("Invalid paramaters sent to set_center!");
            }
            this.geojsmap.center({x: x, y: y});
            this.geojsmap.zoom(z);

            return [x, y, z];
        };


        return Map;
    });
