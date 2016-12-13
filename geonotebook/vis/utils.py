def generate_colormap(colormap, minimum, maximum):
    # A colormap can be a list of dicts
    # or a matplotlib colormap. Either case
    # the returned object will be a list of dicts.
    # from pudb.remote import set_trace; set_trace(term_size=(283, 87))
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
