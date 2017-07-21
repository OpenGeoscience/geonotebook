import os

import ipykernel
from rasterio.warp import transform

# Note:  There isn't a better way to do this? Maybe checking kernel against
# keys/values in kernel_manager class?
# See: (https://stackoverflow.com/questions/12544056/how-to-i-get-the-
# current-ipython-notebook-name)


def get_kernel_id(kernel):
    connection_file_path = ipykernel.get_connection_file()
    connection_file = os.path.basename(connection_file_path)
    return connection_file.split('-', 1)[1].split('.')[0]


def transform_coordinates(source_srs, target_srs, x, y):
    return tuple(i[0] for i in transform(source_srs, target_srs, x, y))
