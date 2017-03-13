import _ from 'underscore';
import parseFunction from 'parse-function';

const app = parseFunction({
  ecmaVersion: 2017
});

function get_default (value) {
  if (_.isUndefined(value)) {
    return false;
  }
  try {
    return eval(value); // eslint-disable-line no-eval
  } catch (e) {
    console.warn(`Could not evaluate "${value}"`);
    return false;
  }
}

function annotate (fn) {
  let parsed;

  parsed = app.parse(fn);

  if (!parsed.isValid) {
    console.warn('Could not parse function');
    return [];
  }

  fn.$arg_meta = _.map(parsed.args, (param) => {
    return {
      key: param,
      default: get_default(parsed.defaults[param])
    };
  });

  return fn.$arg_meta;
}

export default annotate;
