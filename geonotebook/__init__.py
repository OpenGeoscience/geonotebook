import os
import sys
from jinja2 import ChoiceLoader, PackageLoader, PrefixLoader

def _jupyter_server_extension_paths():
    return [{
        "module": "geonotebook"
    }]

def _jupyter_nbextension_paths():
    return [dict(
        section="notebook",
        src="static",
        # directory in the `nbextension/` namespace
        dest="geonotebook",
        # _also_ in the `nbextension/` namespace
        require="geonotebook/index")]

def get_notebook_jinja2_loader(nbapp):
    """Return the appropriate jinja2 template loader for the notebook app.

    This is confusing but necessary to meet the following criteria:
    - Templates in geonotebook/templates will override those in core notebook templates
    - Core notebook templates can still be referred to/extended by referring to them as core@template.html

    The ChoiceLoader tries each of the loaders in turn until one of them provides the right template.
    The PrefixLoader allows us to refer to core templates using the core@ prefix, this is necessary
    because we want to extend templates of the same name while referring to templates in a different loader (core).
    The PackageLoader lets us put our templates ahead in priority of the notebooks templates.
    The core_loader is last which falls back to the original loader the notebook uses.

    This implementation is weird, but should be compatible/composable with other notebook extensions
    and fairly future proof.

    :param nbapp: NotebookApp instance
    :returns: A jinja2 loader designed to work with our notebook templates
    :rtype: jinja2.ChoiceLoader
    """
    return ChoiceLoader([
        PrefixLoader({'core': nbapp.web_app.settings['jinja2_env'].loader}, delimiter='@'),
        PackageLoader('geonotebook'),
        nbapp.web_app.settings['jinja2_env'].loader])

def load_jupyter_server_extension(nbapp):
    nbapp.log.info("geonotebook module enabled!")
    nbapp.web_app.settings['jinja2_env'].loader = get_notebook_jinja2_loader(nbapp)

### Note:  How to add custom web handlers
#     webapp = nbapp.web_app
#     base_url = webapp.settings['base_url']
#
#     webapp.add_handlers(".*$", [
#         (ujoin(base_url, r"/nbextensions"), NBExtensionHandler),
#         (ujoin(base_url, r"/nbextensions/"), NBExtensionHandler),
#         (ujoin(base_url, r"/nbextensions/config/rendermd/(.*)"),
#          RenderExtensionHandler),
#     ])

###   Note: Ugly hack to add geonotebook template to jinja2 search path
#     nbapp.web_app.settings['jinja2_env'].loader.searchpath = [u"/home/kotfic/src/jupyter/geonotebook/geonotebook/templates"] + nbapp.web_app.settings['jinja2_env'].loader.searchpath
