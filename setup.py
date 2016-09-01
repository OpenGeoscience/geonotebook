from setuptools import setup, find_packages
import sys
import tempfile
import os
import json
import shutil

setup(
    name='geonotebook',
    version='0.0.0-prealpha',
    description='A Jupyter notebook extension for Geospatial Analysis',
    long_description='A Jupyter notebook extension for Geospatial Analysis',
    url='https://github.com/OpenDataAnalytics',
    author='Kitware Inc',
    author_email='chris.kotfila@kitware.com',
    license='Apache License 2.0',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    data_files=[('config', ['geonotebook.ini'])],
    entry_points={
        'geonotebook.wrappers.raster': [
            'geotiff = geonotebook.wrappers.image:GeoTiffImage',
            'tiff = geonotebook.wrappers.image:GeoTiffImage',
            'tif = geonotebook.wrappers.image:GeoTiffImage'
        ]

    }



)


# Install the kernel spec when we install the package
from ipykernel import kernelspec
from jupyter_client.kernelspec import KernelSpecManager

KERNEL_NAME = 'geonotebook%i' % sys.version_info[0]

path = os.path.join(tempfile.mkdtemp(suffix='_kernels'), KERNEL_NAME)
try:
    os.makedirs(path)
except OSError:
    pass

kernel_dict = {
    'argv': kernelspec.make_ipkernel_cmd(mod='geonotebook'),
    'display_name': 'Geonotebook (Python %i)' % sys.version_info[0],
    'language': 'python',
}

with open(os.path.join(path, 'kernel.json'), 'w') as fh:
    json.dump(kernel_dict, fh, indent=1)

ksm = KernelSpecManager()
dest = ksm.install_kernel_spec(
    path, kernel_name=KERNEL_NAME, user=False, prefix=sys.prefix)

shutil.rmtree(path)
