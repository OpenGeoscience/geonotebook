import * as jsonrpc from 'geonotebook/jsonrpc';
import expect from 'expect.js';

describe('jsonrpc', function () {
  describe('annotate', function () {
    it('empty function', function () {
      expect(jsonrpc.annotate(function () {})) // eslint-disable-line underscore/prefer-noop
        .to.eql([]);
    });
  });
});
