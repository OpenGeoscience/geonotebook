import ConfigParser
import pkg_resources as pr
import vis
import os, sys

def get_config(path=None):
    conf = ConfigParser.ConfigParser()
    paths = [
        "${GEONOTEBOOK_INI}",
        os.path.join(os.getcwd(), ".geonotebook.ini"),
        "~/.geonotebook.ini",
        os.path.join(sys.prefix, "etc/geonotebook.ini"),
        "/etc/geonotebook.ini"
    ]
    found = False

    if path is not None:
        conf.read(path)
    else:
        for p in paths:
            try:
                with open(os.path.expanduser(
                        os.path.expandvars(p)), 'r') as fh:
                    conf.readfp(fh)
                    found = True
            except IOError:
                pass

            if found:
                break

        if found is False:
            raise RuntimeError("Could not locate configuration file!")

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
