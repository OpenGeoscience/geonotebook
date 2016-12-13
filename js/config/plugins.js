var webpack = require('webpack');
var ExtractTextPlugin = require('extract-text-webpack-plugin');

var define_plugin = new webpack.DefinePlugin({
  GEO_SHA: '""',
  GEO_VERSION: '""'
});

module.exports = [
  define_plugin,
  new ExtractTextPlugin('styles.css')
];
