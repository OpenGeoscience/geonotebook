import _ from 'underscore';

function request (method, params, opts) {
  opts = _.defaults((typeof opts === 'undefined') ? {} : opts,
                          {jsonrpc: '2.0'});

  return _.extend({
    method: method,
    params: params}, opts);
}

export default request;
