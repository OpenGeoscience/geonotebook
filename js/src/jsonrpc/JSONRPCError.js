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

export default JSONRPCError;
