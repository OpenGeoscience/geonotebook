/* global requirejs */

import { Geonotebook, provenance } from 'geonotebook';

if (window.require) {
  window.require.config({
    map: {
      '*': {
        geonotebook: 'nbextensions/geonotebook/index'
      }
    }
  });
}

function load_ipython_extension () {
  return new Promise(function (resolve) {
    requirejs([
      'base/js/namespace',
      'base/js/events'
    ], function (Jupyter, events) {
      if (Jupyter.kernelselector.current_selection === 'geonotebook2' ||
            Jupyter.kernelselector.current_selection === 'geonotebook3') {
        Jupyter.geonotebook = new Geonotebook(Jupyter, events);

        provenance(Jupyter, events);
      }
      console.log('loaded geonotebook');
      resolve();
    });
  });
}

module.exports = {
  load_ipython_extension
};
