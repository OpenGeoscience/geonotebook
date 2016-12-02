var _ = require('underscore');

var karma_config = require('./config/karma');

/**
 * Return URL friendly browser string
 */
function browser (b) {
  return b.toLowerCase().split(/[ /-]/)[0];
}

karma_config.reporters = ['progress', 'coverage'];
karma_config.coverageReporter = {
  reporters: [
    {type: 'html', dir: 'coverage/', subdir: browser},
    {type: 'lcovonly', dir: 'coverage/', subdir: browser},
    {type: 'text'}
  ]
};

var babel_loader = _.findWhere(karma_config.webpack.module.loaders, {loader: 'babel-loader'});
babel_loader.query.plugins = [[
  'istanbul', {
    exclude: [
      'test/**', 'node_modules/**'
    ]
  }
]];

module.exports = function (config) {
  config.set(karma_config);
};
