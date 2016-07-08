define(
    ["jquery",
     "underscore",
     "require",
     "./lib/geo",
     "./lib/utils"],
    function($, _, require, geo, utils){
        var Map = function(notebook, div){
            this.notebook = notebook;
            this.geo = geo;

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

            this.geojsmap.geoOn('geo_select', this.set_region.bind(this));

        };

        Map.prototype.set_region = function(event, args){

            var ul = this.geojsmap.displayToGcs(event.display.upperLeft, "EPSG:4326");
            var lr = this.geojsmap.displayToGcs(event.display.lowerRight, "EPSG:4326");

            this.notebook._remote.set_region(ul.x, ul.y, lr.x, lr.y);


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
            this.geojsmap.center({x: x, y: y});
            this.geojsmap.zoom(z);
        };


        return Map;
    });
