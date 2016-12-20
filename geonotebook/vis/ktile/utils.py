import ipykernel
import os
import requests
#from geonotebook.config import Config


def serialize_config(kConfig):
    return {
        "cache": kConfig.cache.__dict__,
        "layers": {n: serialize_layer(l) for n, l in kConfig.layers.items()}
    }

# Layer is a KTile layer,  NOT a geonotebook layer.
def serialize_layer(kLayer):
    return {"__str__": str(kLayer)}



# Layer is a geonotebook layer, NOT a KTile layer.
# def get_layer_vrt_path(gLayer):
#     config = Config()
#
#     request_url = "{}/{}/{}".format(config.vis_server.base_url,
#                                     get_kernel_id, gLayer.name)
#
#     r = requests.get(request_url)
