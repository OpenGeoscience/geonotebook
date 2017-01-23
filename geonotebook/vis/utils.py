def generate_colormap(colormap, minimum, maximum):
    # A colormap can be a list of dicts
    # or a matplotlib colormap. Either case
    # the returned object will be a list of dicts.
    def range_count(start, stop, count):
        """Generate a list.

        Use the given start stop and count with linear spacing
        e.g. range_count(1, 3, 5) = [1., 1.5, 2., 2.5, 3.]
        """
        step = (stop - start) / float(count - 1)
        return [start + i * step for i in range(count)]

    def rgba2hex(rgba):
        """Convert rgba values to hex."""
        # Slice the tuple so that
        # we don't get alpha and
        # convert values to 8 bit ints
        rgb = tuple([min(max(int(255 * i), 0), 255) for i in rgba[:3]])
        return "#{0:02x}{1:02x}{2:02x}".format(*rgb)

    # If colormap is an iterable return it
    # Sld code has checks for this anyway
    # So an arbitrary iterable won't work
    # anyways
    if hasattr(colormap, '__iter__'):
        return colormap
    else:
        col_list = ['#00007f', '#0000ff', '#0063ff', '#00d4ff', '#4dffa9',
                    '#a9ff4d', '#ffe500', '#ff7c00', '#ff1300', '#7f0000']
        quan_list = range_count(minimum, maximum, len(col_list))

        if hasattr(colormap, '__call__') and hasattr(colormap, 'N'):
            quan_list = range_count(minimum, maximum, colormap.N)
            col_list = [rgba2hex(colormap(i)) for i in range(colormap.N)]

        colormap = [
            {'color': c, 'quantity': q}
            for c, q in zip(col_list, quan_list)
        ]

        return colormap


class RasterStyleOptions(object):
    def __init__(self, opacity=1.0, gamma=1.0, projection='EPSG:3857',
                 kernel_id=None, zIndex=None, colormap=None, interval=None,
                 layer_type=None, **kwargs):

        # self.vis_url = vis_url
        self.opacity = opacity
        self.projection = projection
        self.gamma = gamma
        self.interval = interval
        self.colormap = None
        self.zIndex = zIndex
        self.kernel_id = kernel_id
        self.layer_type = layer_type

        if colormap is None:
            self.colormap = []
        else:
            # If we have the colormap in the form
            # of a list of dicts with color/quantity then
            # set options['colormap'] equal to this
            for d in colormap:
                assert 'color' in d
                assert 'quantity' in d
            self.colormap = colormap

    @staticmethod
    def get_colormap(data, mpl_cmap, **kwargs):
        try:
            _min, _max = kwargs.get("interval", None)
        except TypeError:
            _min, _max = None, None

        if _min is None:
            try:
                _min = min(data.min)
            except (ValueError, TypeError):
                _min = data.min

        if _max is None:
            try:
                _max = max(data.max)
            except (ValueError, TypeError):
                _max = data.max

        return generate_colormap(mpl_cmap, _min, _max)

    def serialize(self):
        return {
            'layer_type': self.layer_type,
            'opacity': self.opacity,
            'gamma': self.gamma,
            'projection': self.projection,
            'interval': self.interval,
            'colormap': self.colormap,
            'kernel_id': self.kernel_id,
            'zIndex': self.zIndex
        }

    def __hash__(self):
        return hash((
            self.layer_type,
            self.opacity,
            self.gamma,
            self.interval,
            self.projection,
            tuple(tuple(c.items()) for c in self.colormap),
            self.kernel_id,
            self.zIndex))
