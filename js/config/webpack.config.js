var loaders = require('./loaders');
var resolve = require('./resolve');
var plugins = require('./plugins');

module.exports = [
  {
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
    plugins: plugins
  }
];
