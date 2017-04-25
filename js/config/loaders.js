var ExtractTextPlugin = require('extract-text-webpack-plugin');
module.exports = [
  {
    test: /.js$/,
    loader: 'babel-loader',
    exclude: /node_modules/,
    query: {
      presets: [],
      plugins: ['transform-es2015-modules-commonjs']
    }
  }, {
    test: /.js$/,
    loader: 'unlazy'
  }, {
    test: /ol\/.*\.js$/,
    loader: 'babel-loader',
    query: {
      presets: [],
      plugins: ['transform-es2015-modules-commonjs']
    }
  }, {
    test: /\.css$/,
    exclude: /node_modules/,
    loaders: [
      ExtractTextPlugin.extract('style-loader', 'css-loader'),
      'css-loader'
    ]
  }, {
    test: /geojs\/.*\.styl$/,
    loader: 'style-loader!css-loader!stylus-loader'
  }, {
    test: /\.json$/,
    loader: 'json-loader'
  }, {
    test: /vgl\.js$/,
    loader: 'expose?vgl!imports?mat4=gl-mat4,vec4=gl-vec4,vec3=gl-vec3,vec2=gl-vec2,$=jquery'
  }
];
