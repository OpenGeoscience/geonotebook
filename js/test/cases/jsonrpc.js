import * as jsonrpc from 'geonotebook/jsonrpc';
import expect from 'expect.js';

describe('jsonrpc', function () {
  describe('annotate', function () {
    it('empty function', function () {
      expect(jsonrpc.annotate(function () {}))
        .to.eql([]);
    });
    it('one argument', function () {
      expect(jsonrpc.annotate(function (a) {}))
        .to.eql([{ key: 'a', default: false }]);
    });
    it('two arguments', function () {
      expect(jsonrpc.annotate(function (a, b) {}))
        .to.eql([{
          key: 'a',
          default: false
        }, {
          key: 'b',
          default: false
        }]);
    });
    it('default argument', function () {
      expect(jsonrpc.annotate(function (a = 0) {}))
        .to.eql([{ key: 'a ', default: ' 0' }]);
    });
    it('required and default arguments', function () {
      expect(jsonrpc.annotate(function (req_arg, opt_arg = 'the value') {}))
        .to.eql([{
          key: 'req_arg',
          default: false
        }, {
          key: 'opt_arg ',
          default: " 'the value'"
        }]);
    });
  });
});
