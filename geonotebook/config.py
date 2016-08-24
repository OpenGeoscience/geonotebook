import ConfigParser
import pkg_resources as pr
import vis

def get_config(path=None):
    conf = ConfigParser.ConfigParser()
    if path is not None:
        conf.read(path)
    else:

        # Should check
        # ./.geonotebook.ini
        # ~/.geonotebook.ini
        # {sys.prefix}/etc/geonotebook.ini
        # /etc/geonotebook.ini
        # GEONOTEBOOK_INI environment variable
        # pkg_resources.resource_stream('geonotebook', 'config/geonotebook.ini')

        conf.readfp(pr.resource_stream('geonotebook', 'config/geonotebook.ini'))

    return conf


class Config(object):
    _valid_vis_hash = {
        "geoserver": vis.Geoserver
    }

    def __init__(self, path=None):
        self.config = get_config(path)

    @property
    def vis_server(self):
        vis_server_section = self.config.get("default", "vis_server")
        try:
            cls = self._valid_vis_hash[vis_server_section]
        except KeyError:
            raise NotImplemented("{} is not a valid vis_server".format(
                vis_server_section))

        return cls(**dict(self.config.items(vis_server_section)))
