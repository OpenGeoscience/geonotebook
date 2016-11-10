from ipykernel.ipkernel import IPythonKernel
import logging
import os
from logging.handlers import SysLogHandler

from inspect import getmembers, ismethod, isfunction, getargspec
from promise import Promise
from types import MethodType

from . import jsonrpc
from .jsonrpc import (json_rpc_request,
                      json_rpc_notify,
                      json_rpc_result,
                      is_response,
                      is_request,
                      rpc,
                      RemoteMixin)

from .layers import (BBox,
                     GeonotebookLayerCollection,
                     NoDataLayer,
                     AnnotationLayer,
                     SimpleLayer,
                     TimeSeriesLayer)

from .wrappers import RasterData, RasterDataCollection

@rpc.endpoints('add_annotation')
class Geonotebook(RemoteMixin, object):

    @property
    def log(self):
        return self._kernel.log

    def __init__(self, kernel, *args, **kwargs):
        super(Geonotebook, self).__init__(*args, **kwargs)
        self.view_port = None
        self.x = None
        self.y = None
        self.z = None
        self.layers = GeonotebookLayerCollection([])

        self._kernel = kernel

    def rpc_error(self, error):
        self.log.error("JSONRPCError (%s): %s" % (error['code'], error['message']))


    ### Remote RPC wrappers ###

    def set_center(self, x, y, z):
        def _set_center(result):
            self.x, self.y, self.z = result

        return self.remote.set_center(x, y, z).then(_set_center, self.rpc_error)

    def add_layer(self, data, name=None, vis_url=None, layer_type='wms',
                  **kwargs):



        # Create the GeonotebookLayer -  if vis_url is none,  this will take
        # data_path and upload it to the configured vis_server,  this will make
        # the visualization url available through the 'vis_url' attribute
        # on the layer object.

        # HACK:  figure out a way to do this without so many conditionals
        if isinstance(data, RasterData):
            # TODO verify layer exists in geoserver?
            name = data.name if name is None else name

            layer = SimpleLayer(name, data=data, vis_url=vis_url, **kwargs)
        elif isinstance(data, RasterDataCollection):
            assert name is not None, \
                RuntimeError("RasterDataCollection layers require a 'name'")

            layer = TimeSeriesLayer(name,  data=data, vis_url=vis_url, **kwargs)

        else:
            assert name is not None, \
                RuntimeError("Non data layers require a 'name'")
            if layer_type == 'annotation':
                layer = AnnotationLayer(name, self.layers, **kwargs)
            else:
                layer = NoDataLayer(name, vis_url=vis_url, **kwargs)

        def _add_layer(layer_name):
            self.layers.append(layer)

        # These should be managed by some kind of handler to allow for
        # additional types to be added more easily
        if layer_type == 'wms':
            params = layer.params
            params['zIndex'] = len(self.layers)

            cb = self.remote.add_wms_layer(layer.name, layer.vis_url, params)\
                .then(_add_layer, self.rpc_error)
        elif layer_type == 'osm':
            params = {'zIndex': len(self.layers)}

            cb = self.remote.add_osm_layer(layer.name, layer.vis_url, params)\
                .then(_add_layer, self.rpc_error)
        elif layer_type == 'annotation':
            params = layer.params

            cb = self.remote.add_annotation_layer(layer.name, params)\
                .then(_add_layer, self.rpc_error)
        else:
            # Exception?
            pass

        return cb

    def remove_layer(self, layer_name):
        # If layer_name is an object with a 'name' attribute we assume
        # thats the layer you want removed.  This allows us to pass in
        # GeonotebookLayer objects,  as well as regular string layer names
        if hasattr(layer_name, 'name'):
            layer_name = layer_name.name

        def _remove_layer(layer_name):
            self.layers.remove(layer_name)

        cb = self.remote.remove_layer(layer_name).then(
            _remove_layer, self.rpc_error)

        return cb


    def add_annotation(self, ann_type, coords, meta):
        self.layers.annotation.add_annotation(ann_type, coords, meta)
        return True




class GeonotebookKernel(IPythonKernel):
    def _unwrap(self, msg):
        """Unwrap a Comm message

        Remove the Comm envolpe and return an RPC message

        :param msg: the Comm message
        :returns: An RPC message
        :rtype: dict

        """

        return msg['content']['data']

    def handle_comm_msg(self, message):
        """Handler for incomming comm messages

        :param msg: a Comm message
        :returns: Nothing
        :rtype: None

        """
        msg = self._unwrap(message)

        try:
            rpc.recv_msg(msg)

        except jsonrpc.JSONRPCError as e:
            rpc.send_msg(json_rpc_result(None, e.toJson(), msg['id']))
            self.log.error(u"JSONRPCError (%s): %s" % (e.code, e.message))

        except Exception as e:
            self.log.error(u"Error processing msg: {}".format(str(e)))


    def handle_comm_open(self, comm, msg):
        """Handler for opening a comm

        :param comm: The comm to open
        :param msg: The initial comm_open message
        :returns: Nothing
        :rtype: None

        """
        self.comm = comm
        self.comm.on_msg(self.handle_comm_msg)

        rpc.set_remote_protocol(comm, self._unwrap(msg))

        # TODO: HACK until we actually implement object routing
        rpc.geonotebook = self.geonotebook

        # Reply to the open comm,  this should probably be set up on
        # self.geonotebook._remote as an actual proceedure call
        self.comm.send({
            "method": "set_protocol",
            "data": rpc.get_protocol()
        })

        # THis should be handled in a callback that is fired off
        # When set protocol etc is complete.
        self.geonotebook.add_layer(
            None, name="osm_base", layer_type="osm",
            vis_url="http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
            system_layer=True)

        self.geonotebook.add_layer(
            None, name="annotation",
            layer_type="annotation", vis_url=None,
            system_layer=True, expose_as="annotation")


    def do_shutdown(self, restart):
        self.geonotebook = None;

        super(GeonotebookKernel, self).do_shutdown(restart)

        if restart:
            self.geonotebook = Geonotebook(self)
            self.shell.user_ns.update({'M': self.geonotebook})


    def start(self):
        self.geonotebook = Geonotebook(self)
        self.shell.user_ns.update({'M': self.geonotebook})
        super(GeonotebookKernel, self).start()


    def __init__(self, **kwargs):
        kwargs['log'].setLevel(logging.DEBUG)
        self.log = kwargs['log']

        super(GeonotebookKernel, self).__init__(**kwargs)

        self.comm_manager.register_target('geonotebook', self.handle_comm_open)
