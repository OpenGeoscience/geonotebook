import _ from 'underscore';

function JSONRPCError (code) {
  return function (message, data) {
    console.log('JSONRPCError (' + code + '): ' + message);

    if (data !== undefined) {
      return {
        code: code,
        message: message,
        data: data
      };
    } else {
      return {
        code: code,
        message: message
      };
    }
  };
}

function request (method, params, opts) {
  opts = _.defaults((typeof opts === 'undefined') ? {} : opts,
                          {jsonrpc: '2.0'});

  return _.extend({
    method: method,
    params: params}, opts);
}

function response (result, error, id) {
        // TODO validate taht result/error are mutually exclusive
  return {result: result,
    error: error,
    id: id };
}

function is_request (msg) {
  return 'method' in msg && 'params' in msg && 'id' in msg;
}

function is_response (msg) {
  return 'result' in msg && 'error' in msg && 'id' in msg;
}

const ParseError = JSONRPCError(-32700);
const InvalidRequest = JSONRPCError(-32600);
const MethodNotFound = JSONRPCError(-32601);
const InvalidParams = JSONRPCError(-32602);
const InternalError = JSONRPCError(-32603);
const ServerError = JSONRPCError(-32000);

export {
  JSONRPCError,
  request,
  response,
  is_request,
  is_response,
  ParseError,
  InvalidRequest,
  MethodNotFound,
  InvalidParams,
  InternalError,
  ServerError
};
