var path = require('path');

var renderer = process.env.GEONOTEBOOK_MAP_RENDERER || 'geojs';

module.exports = {
  alias: {
    geonotebook: path.resolve(__dirname, '..', 'src'),
    map_renderer: 'geonotebook/map/' + renderer,
    geojs: 'geojs/src',
    jquery: 'jquery/dist/jquery',
    proj4: 'proj4/lib',
    vgl: 'vgl/vgl.js',
    d3: 'd3/d3.js',
    mousetrap: 'mousetrap/mousetrap.js'
  }
};
