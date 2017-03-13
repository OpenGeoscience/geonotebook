import _ from 'underscore';
import * as jsonrpc from 'geonotebook/jsonrpc';
import expect from 'expect.js';

describe('jsonrpc', function () {
  describe('annotate', function () {
    const warn = console.warn;
    var message;

    beforeEach(function () {
      message = null;
      console.warn = function (msg) {
        message = msg;
      };
    });

    afterEach(function () {
      console.warn = warn;
    });

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
        .to.eql([{ key: 'a', default: 0 }]);
    });
    it('required and default arguments', function () {
      expect(jsonrpc.annotate(function (req_arg, opt_arg = 'the value') {}))
        .to.eql([{
          key: 'req_arg',
          default: false
        }, {
          key: 'opt_arg',
          default: 'the value'
        }]);
    });
    it('handle undefined', function () {
      expect(jsonrpc.annotate(undefined))
        .to.eql([]);
      expect(message).to.match(/Could not parse/);
    });
    it('handle lambda functions', function () {
      expect(jsonrpc.annotate((a, b = 0) => a))
        .to.eql([{
          key: 'a',
          default: false
        }, {
          key: 'b',
          default: 0
        }]);
    });
    it('handle class functions', function () {
      class A {
        func (a, b = 0) {
          return a;
        }
      }
      const a = new A();

      expect(jsonrpc.annotate(a.func))
        .to.eql([{
          key: 'a',
          default: false
        }, {
          key: 'b',
          default: 0
        }]);
    });
    it('handle a class function containing an arrow function', function () {
      // This is tested because of an edge case in the function parsing
      // method.  https://github.com/tunnckoCore/parse-function/issues/30

      class A {
        func (a, b = 0) {
          return () => a;
        }
      }
      const a = new A();

      expect(jsonrpc.annotate(a.func))
        .to.eql([{
          key: 'a',
          default: false
        }, {
          key: 'b',
          default: 0
        }]);
    });
    it('handle non-literal defaults', function () {
      var b = _.constant(0);
      function test (a = b()) {
      }
      expect(jsonrpc.annotate(test))
        .to.eql([{
          key: 'a',
          default: false
        }]);
      expect(message).to.match(/Could not evaluate/);
    });
  });
});
