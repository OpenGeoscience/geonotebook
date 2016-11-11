var loaders = [
  { test: /.js$/, loader: 'babel-loader' }
];
var resolve = {
  alias: {
    geonotebook: './src'
  }
};

var buildExtension = require('@jupyterlab/extension-builder/lib/builder').buildExtension;

buildExtension({
  name: 'jupyter-geonotebook',
  entry: './src/labplugin',
  outputDir: '../geonotebook/static',
  useDefaultLoaders: false,
  config: {
    module: {
      loaders: loaders
    },
    resolve: resolve
  }

});

module.exports = [
  {// Notebook extension
    entry: './src/index',
    output: {
      filename: 'geonotebook.js',
      path: '../geonotebook/static',
      libraryTarget: 'amd'
    }
  }
];
