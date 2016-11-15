define(
    ["jquery",
     "underscore",
     "require",
     "base/js/events",
     "./lib/jsonrpc",
     "./lib/geo",
     "./lib/utils"],
    function($, _, require, events, jsonrpc, geo, utils){
        var Map = function(notebook, div){
            this.notebook = notebook;
            this.geo = geo;
            this.geojsmap = null;
            this.region = null;
            this.annotation_color_palette = ['#db5f57', // {r:219, g: 95, b: 87}
                                             '#dbae57', // {r:219, g:174, b: 87}
                                             '#b9db57', // {r:185, g:219, b: 87}
                                             '#69db57', // {r:105, g:219, b: 87}
                                             '#57db94', // {r: 87, g:219, b:148}
                                             '#57d3db', // {r: 87, g:211, b:219}
                                             '#5784db', // {r: 87, g:132, b:219}
                                             '#7957db', // {r:121, g: 87, b:219}
                                             '#c957db', // {r:201, g: 87, b:219}
                                             '#db579e'] // {r:219, g: 87, b:158}
            this._color_counter = -1;

            events.on('geonotebook.protocol_negotiation_complete', function(event, router){
                this.remote = router.remote_factory(this);

                $('#geonotebook-map').empty();
                this.geojsmap = geo.map({node: '#geonotebook-map',
                                         width: $("#geonotebook-map").width(),
                                         height: $("#geonotebook-map").height(),
                                         allowRotation: false
                                        });
            }.bind(this));

        };

        jsonrpc.router.register_class(Map, "geonotebook.kernel.Geonotebook");

        Map.prototype.next_color = function(){
            this._color_counter = this._color_counter + 1;

            var idx = this._color_counter % this.annotation_color_palette.length

            return this.annotation_color_palette[idx]
        }

        Map.prototype.rpc_error = function(error){
            console.log("JSONRPCError(" + error.code + "): " + error.message);
        };


        Map.prototype.msg_types = ["get_protocol",
                                   "set_center",
                                   "_debug",
                                   "add_wms_layer",
                                   "replace_wms_layer",
                                   "add_osm_layer",
                                   "add_annotation_layer",
                                   "clear_annotations",
                                   "remove_layer"];

        Map.prototype._debug = function(msg){
            console.log(msg);
        };

        // Generate a list of protocol definitions for the white listed functions
        // in msg_types. This will be passed to the Python geonotebook object and
        // will initialize its RPC object so JS map frunctions can be called from
        // the Python environment.

        Map.prototype.get_protocol = function(){
            return this.msg_types.map(function(msg_type){

                var args = utils.annotate(this[msg_type]);

                return {procedure: msg_type,
                        required: args.filter(function(arg){ return !arg.default;  }),
                        optional: args.filter(function(arg){ return !!arg.default; }) };


            }.bind(this));

        };

        Map.prototype.set_center = function(x, y, z){
            if ( x < -180.0 || x > 180.0 || y < -90.0 || y > 90.0) {
                throw new jsonrpc.InvalidParams("Invalid parameters sent to set_center!");
            }
            this.geojsmap.center({x: x, y: y});
            this.geojsmap.zoom(z);

            return [x, y, z];
        };


        Map.prototype.get_layer = function(layer_name){
            return _.find(this.geojsmap.layers(),
                          function(l){ return l.name() == layer_name; });
        };

        Map.prototype.remove_layer = function(layer_name) {
            this.geojsmap.deleteLayer(this.get_layer(layer_name));
            return layer_name;
        };


        Map.prototype.clear_annotations = function() {
            var annotation_layer = this.get_layer("annotation");
            return annotation_layer.removeAllAnnotations();
        }


        Map.prototype.add_annotation = function(annotation){
            annotation.options("style").fillColor = this.next_color();
            annotation.options("style").fillOpacity = 0.8;
            annotation.options("style").strokeWidth = 2;

            var annotation_meta = {
                id: annotation.id(),
                name: annotation.name(),
                rgb: annotation.options("style").fillColor
            };

            this.remote.add_annotation(
                annotation.type(),
                annotation.coordinates("EPSG:4326"),
                annotation_meta
            ).then(
                function(result){
                    annotation.layer().modified();
                    annotation.draw();
                }.bind(this),
                this.rpc_error.bind(this));

        };

        // Note: point/polygon's fire 'state' when they are added to
        //       the map,  while rectangle's fire 'add'
        // See:  https://github.com/OpenGeoscience/geojs/issues/623
        Map.prototype.add_annotation_handler = function(evt) {
            var annotation = evt.annotation;
            if (annotation.type() === "rectangle") {
                this.add_annotation(annotation);
            }

        };
        Map.prototype.state_annotation_handler = function(evt) {
            var annotation = evt.annotation;
            if(annotation.type() === "point" || annotation.type() === "polygon") {
                this.add_annotation(annotation);
            }

        };

        Map.prototype.add_annotation_layer = function(layer_name, params){
            var layer = this.geojsmap.createLayer('annotation', {
                annotations: ['rectangle', 'point', 'polygon']
            });
            layer.name(layer_name);



            layer.geoOn(geo.event.annotation.add, this.add_annotation_handler.bind(this));
//            layer.geoOn(geo.event.annotation.remove, handleAnnotationChange);
            layer.geoOn(geo.event.annotation.state, this.state_annotation_handler.bind(this));

            layer.geoOn('geonotebook:rectangle_annotation_mode', function(evt) {
                layer.mode('rectangle');
            });

            layer.geoOn('geonotebook:point_annotation_mode', function(evt) {
                layer.mode('point');
            });

            layer.geoOn('geonotebook:polygon_annotation_mode', function(evt) {
                layer.mode('polygon');
            });


            return layer_name;
        }

        Map.prototype._set_layer_zindex = function(layer, index){
            if( index !== undefined ){
                var annotation_layer = this.get_layer("annotation");
                layer.zIndex(index);
                if( annotation_layer !== undefined ){
                    // Annotation layer should always be on top
                    var max = _.max(_.map(this.geojsmap.layers(), (e) => e.zIndex()));
                    annotation_layer.zIndex(max + 1);
                }

            }
        };

        Map.prototype.add_osm_layer = function(layer_name, url, params){
            var osm = this.geojsmap.createLayer('osm');

            osm.name(layer_name);
            osm.url = url;

            // make sure zindex is explicitly set
            this._set_layer_zindex(osm, params['zIndex']);

            return layer_name
        };

        Map.prototype.replace_wms_layer = function( layer_name, base_url, params){

            var old_layer = _.find(this.geojsmap.layers(), function(e) { return e.name() == layer_name; })

            if (old_layer === undefined){

                console.log("Could not find " + layer_name + " layer");
                return false;

            } else {
                var projection = 'EPSG:3857';

                var wms = this.geojsmap.createLayer('osm', {
                    keepLower: false,
                    attribution: null
                });
                wms.name(layer_name);
                this._set_layer_zindex(wms, old_layer.zIndex());

                wms.url(function (x, y, zoom) {

                    var bb = wms.gcsTileBounds({
                        x: x,
                        y: y,
                        level: zoom
                    }, projection);

                    var bbox_mercator = bb.left + ',' + bb.bottom + ',' +
                            bb.right + ',' + bb.top;


                    var local_params = {
                        'SERVICE': 'WMS',
                        'VERSION': '1.3.0',
                        'REQUEST': 'GetMap',
                        //                     'LAYERS': layer_name, // US Elevation
                        'STYLES': '',
                        'BBOX': bbox_mercator,
                        'WIDTH': 512,
                        'HEIGHT': 512,
                        'FORMAT': 'image/png',
                        'TRANSPARENT': true,
                        'SRS': projection,
                        'TILED': true
                        // TODO: What if anythin should be in SLD_BODY?
                     //'SLD_BODY': sld
                    };

                    if( params['SLD_BODY']) {
                        local_params['SLD_BODY'] = params['SLD_BODY'];
                    }

                    return base_url + '&' + $.param(local_params);

                });

                this.geojsmap.deleteLayer(old_layer);

                return true;
            }

        };


        Map.prototype.add_wms_layer = function(layer_name, base_url, params){

            // If a layer with this name already exists,  replace it
            if(this.get_layer(layer_name) !== undefined){
                this.geojsmap.deleteLayer(this.get_layer(layer_name));
            }

            var projection = 'EPSG:3857';

            var wms = this.geojsmap.createLayer('osm', {
                keepLower: false,
                attribution: null
            });

            // make sure zindex is explicitly set
            this._set_layer_zindex(wms, params['zIndex']);

            wms.name(layer_name);

            wms.url(function (x, y, zoom) {

                 var bb = wms.gcsTileBounds({
                     x: x,
                     y: y,
                     level: zoom
                 }, projection);

                 var bbox_mercator = bb.left + ',' + bb.bottom + ',' +
                         bb.right + ',' + bb.top;


                 var local_params = {
                     'SERVICE': 'WMS',
                     'VERSION': '1.3.0',
                     'REQUEST': 'GetMap',
//                     'LAYERS': layer_name, // US Elevation
                     'STYLES': '',
                     'BBOX': bbox_mercator,
                     'WIDTH': 512,
                     'HEIGHT': 512,
                     'FORMAT': 'image/png',
                     'TRANSPARENT': true,
                     'SRS': projection,
                     'TILED': true
                     // TODO: What if anythin should be in SLD_BODY?
                     //'SLD_BODY': sld
                 };

                if( params['SLD_BODY']) {
                    local_params['SLD_BODY'] = params['SLD_BODY'];
                }

                return base_url + '&' + $.param(local_params);

            });

            return layer_name;

        };

        return Map;
    });
