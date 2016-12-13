// See:  https://github.com/webpack/karma-webpack/issues/23
var tests = require.context('./cases', true, /.*\.js$/);
tests.keys().forEach(tests);
