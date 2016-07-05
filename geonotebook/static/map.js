define(
    ["jquery",
     "require",
     "./lib/geo",
     "./lib/utils"],
    function($, require, geo, utils){
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
        };

        Map.prototype.msg_types = ["get_protocol", 'set_center'];

        Map.prototype.get_protocol = function(){
            return this.msg_types.map(function(msg_type){

                var args = utils.annotate(this[msg_type]);

                return {proceedure: msg_type,
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

        };


        return Map;
    });
