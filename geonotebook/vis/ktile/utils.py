import ipykernel
import os
import requests

def serialize_config(kConfig):
    return {
        "cache": kConfig.cache.__dict__,
        "layers": {n: serialize_layer(l) for n, l in kConfig.layers.items()}
    }


def serialize_provider(kProvider):
    try:
        return kProvider.serialize()
    except AttributeError:
        return str(kProvider)

# Layer is a KTile layer,  NOT a geonotebook layer.
def serialize_layer(kLayer):
    return {
        "__str__": str(kLayer),
        "provider": serialize_provider(kLayer.provider)
        # Other layer properties should be added here
    }



# Layer is a geonotebook layer, NOT a KTile layer.
def get_layer_vrt_path(gLayer):

    kernel_id = os.path.basename(
        ipykernel.get_connection_file()).split('-', 1)[1].split('.')[0]

    request_url = "{}/{}/{}".format(gLayer.config.vis_server.base_url,
                                    kernel_id, gLayer.name)

    r = requests.get(request_url)
    response = r.json()

    return response['provider']['vrt_path']


def get_layer_vrt(gLayer):
    with open(get_layer_vrt_path(gLayer), 'r') as fh:
        xml = fh.read()

    return xml
