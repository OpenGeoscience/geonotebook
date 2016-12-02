var loaders = require('./loaders');
var resolve = require('./resolve');
var plugins = require('./plugins');

module.exports = {
  autoWatch: false,
  browsers: [
    'PhantomJS'
  ],
  frameworks: ['mocha'],
  reporters: ['progress', 'mocha'],
  files: [
    'test/all.js',
    {pattern: 'test/data/**/*', included: false},
    {pattern: 'test/cases/**/*.js', included: false, served: false, watched: true}
  ],
  proxies: {
    '/data/': '/base/test/data'
  },
  preprocessors: {
    'test/all.js': ['webpack', 'sourcemap']
  },
  webpack: {
    cache: true,
    devtool: 'inline-source-map',
    module: {
      loaders: loaders
    },
    resolve: resolve,
    plugins: plugins
  }
};
