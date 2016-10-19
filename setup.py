from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.develop import develop
import sys
import tempfile
import os
import json
import shutil
import glob

def post_install(func):
    def command_wrapper(command_subclass):
        # Keep a reference to the command subclasses 'run' function
        _run = command_subclass.run

        def run(self):
            _run(self)
            print("running post install function {}".format(func.__name__))
            func(self)

        command_subclass.run = run
        return command_subclass

    return command_wrapper


def install_kernel(cmd):
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


def install_geonotebook_ini(cmd):

    # cmd.dist is a pkg_resources.Distribution class, See:
    # http://setuptools.readthedocs.io/en/latest/pkg_resources.html#distribution-objects

    # pkg_resources.Distribution.location can be a lot of things,  but in the case of
    # a develop install it will be the path to the source tree. This will not work
    # if applied to more exotic install targets
    # (e.g. pip install -e git@github.com:OpenGeoscience/geonotebook.git)
    base_dir = cmd.dist.location
    # cmd.distribution is a setuptools.dist.Distribution class, See:
    # https://github.com/pypa/setuptools/blob/master/setuptools/dist.py#L215
    for sys_path, local_paths in cmd.distribution.data_files:
        try:
            os.makedirs(os.path.join(sys.prefix, sys_path))
        except OSError:
            pass

        for local_path in local_paths:
            for l in glob.glob(local_path):
                src = os.path.join(base_dir, l)

                dest = os.path.join(sys_path, os.path.basename(src))\
                       if sys_path.startswith("/") else \
                          os.path.join(sys.prefix, sys_path, os.path.basename(src))

                print("copying {} to {}".format(src, dest))

                shutil.copyfile(src, dest)


def install_nbextension(cmd):
    from notebook.nbextensions import (install_nbextension_python,
                                       enable_nbextension)

    install_nbextension_python("geonotebook", overwrite=True, sys_prefix=True)
    enable_nbextension("notebook", "geonotebook/index", sys_prefix=True)


def install_serverextension(cmd):
    from notebook.serverextensions import toggle_serverextension_python
    toggle_serverextension_python('geonotebook', enabled=True, sys_prefix=True)


@post_install(install_serverextension)
@post_install(install_nbextension)
@post_install(install_kernel)
class CustomInstall(install):
    pass


@post_install(install_serverextension)
@post_install(install_nbextension)
@post_install(install_geonotebook_ini)
@post_install(install_kernel)
class CustomDevelop(develop):
    pass


setup(
    name='geonotebook',
    version='0.0.0',
    description='A Jupyter notebook extension for Geospatial Analysis',
    long_description='A Jupyter notebook extension for Geospatial Analysis',
    url='https://github.com/OpenDataAnalytics',
    author='Kitware Inc',
    author_email='chris.kotfila@kitware.com',
    license='Apache License 2.0',
    install_requires=[
        "ipykernel",
        "jupyter_client",
        "notebook"
    ],
    cmdclass={
        'install': CustomInstall,
        'develop': CustomDevelop
    },
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    data_files=[
        ('etc', ['config/geonotebook.ini'])
    ],
    package_data={'geonotebook': ['static/*.js',
                                  'static/lib/*.js',
                                  'static/css/*.css',
                                  'templates/*.html']},
    test_suite="tests",
    entry_points={
        'geonotebook.wrappers.raster': [
            'geotiff = geonotebook.wrappers.image:GeoTiffImage',
            'tiff = geonotebook.wrappers.image:GeoTiffImage',
            'tif = geonotebook.wrappers.image:GeoTiffImage'
        ]

    }
)
