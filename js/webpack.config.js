var webpack = require('webpack');
var ExtractTextPlugin = require('extract-text-webpack-plugin');
var loaders = [
  {
    test: /.js$/,
    loader: 'babel-loader',
    exclude: /node_modules/,
    query: {
      presets: ['es2015']
    }
  }, {
    test: /\.css$/,
    exclude: /node_modules/,
    loaders: [
      ExtractTextPlugin.extract('style-loader', 'css-loader'),
      'css-loader'
    ]
  }, {
    test: /\.json$/,
    loader: 'json-loader'
  }, {
    test: /vgl\.js$/,
    loader: 'expose?vgl!imports?mat4=gl-mat4,vec4=gl-vec4,vec3=gl-vec3,vec2=gl-vec2,$=jquery'
  }
];
var resolve = {
  alias: {
    geonotebook: './index',
    geojs: 'geojs/src',
    jquery: 'jquery/dist/jquery',
    proj4: 'proj4/lib',
    vgl: 'vgl/vgl.js',
    d3: 'd3/d3.js',
    mousetrap: 'mousetrap/mousetrap.js'
  }
};
var define_plugin = new webpack.DefinePlugin({
  GEO_SHA: '""',
  GEO_VERSION: '""'
});

module.exports = [
  {// Notebook extension
    entry: './src/extension',
    output: {
      filename: 'index.js',
      path: '../geonotebook/static',
      libraryTarget: 'amd'
    },
    module: {
      loaders: loaders
    },
    resolve: resolve,
    plugins: [
      define_plugin,
      new ExtractTextPlugin('styles.css')
    ]
  }
];
