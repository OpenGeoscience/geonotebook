import annotate from './annotate';
import request from './request';
import response from './response';
import Remote from './Remote';
import ReplyCallback from './ReplyCallback';
import * as constants from './constants';

function is_request (msg) {
  return 'method' in msg && 'params' in msg && 'id' in msg;
}

function is_response (msg) {
  return 'result' in msg && 'error' in msg && 'id' in msg;
}

export {
  annotate,
  constants,
  request,
  response,
  is_request,
  is_response,
  Remote,
  ReplyCallback
};
