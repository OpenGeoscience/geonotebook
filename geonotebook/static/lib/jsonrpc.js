define(
    ["underscore"],
    function(_){
        var JSONRPCError = function(code){
            return function(message, data){
                if (data !== undefined ){
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
        };


        return {
            request: function(method, params, opts){
                opts = _.defaults((typeof opts === 'undefined') ? {} : opts,
                                  {jsonrpc: "2.0"});

                return _.extend({
                    method: method,
                    params: params,
                    id: "TESTID"}, opts);
            },


            response:  function(result, error, id){
                // TODO validate taht result/error are mutually exclusive
                return {result: result,
                        error: error,
                        id: id };
            },

            is_request: function(msg){
                return 'method' in msg && 'params' in msg && 'id' in msg;
            },

            is_response: function(msg){
                return 'result' in msg && 'error' in msg && 'id' in msg;
            },

            ParseError: JSONRPCError(-32700),
            InvalidRequest: JSONRPCError(-32600),
            MethodNotFound: JSONRPCError(-32601),
            InvalidParams: JSONRPCError(-32602),
            InternalError: JSONRPCError(-32603),
            ServerError: JSONRPCError(-32000)
        };
    });
