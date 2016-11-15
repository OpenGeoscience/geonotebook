// This class stores a JSONRPC message and callbacks which are evaluated
// once the Remote object recieves a 'resolve' call with the message's id.
// This is initialized with a JSONRPC message and a function that takes a
// message and sends it across some transport mechanism (e.g. Websocket).
var ReplyCallback = function (msg, send_message) {
  this.state = 'CREATED';
  this.msg = msg;
  this.send_message = send_message;
};

ReplyCallback.prototype.then = function (reply_handler, error_handler) {
  this.reply_handler = reply_handler;
  this.error_handler = error_handler;

  this.send_message(this.msg);
  this.state = 'PENDING';
};

export default ReplyCallback;
