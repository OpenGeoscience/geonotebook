var ExtractTextPlugin = require('extract-text-webpack-plugin');
module.exports = [
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
