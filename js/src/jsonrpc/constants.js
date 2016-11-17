import JSONRPCError from './JSONRPCError';

const ParseError = JSONRPCError(-32700);
const InvalidRequest = JSONRPCError(-32600);
const MethodNotFound = JSONRPCError(-32601);
const InvalidParams = JSONRPCError(-32602);
const InternalError = JSONRPCError(-32603);
const ServerError = JSONRPCError(-32000);

export {
  ParseError,
  InvalidRequest,
  MethodNotFound,
  InvalidParams,
  InternalError,
  ServerError
};
