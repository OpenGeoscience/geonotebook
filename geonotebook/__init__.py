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



def load_jupyter_server_extension(nbapp):
#    import pudb; pu.db
    nbapp.log.info("geonotebook module enabled!")

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
