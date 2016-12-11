from distutils import log
import glob
import json
import os
import shutil
from subprocess import check_call
import sys
import tempfile

from setuptools import Command, find_packages, setup
from setuptools.command.build_py import build_py
from setuptools.command.develop import develop
from setuptools.command.egg_info import egg_info
from setuptools.command.install import install
from setuptools.command.sdist import sdist


def post_install(func):
    def command_wrapper(command_subclass):
        # Keep a reference to the command subclasses 'run' function
        _run = command_subclass.run

        def run(self):
            _run(self)
            log.info("running post install function {}".format(func.__name__))
            func(self)

        command_subclass.run = run
        return command_subclass

    return command_wrapper


def install_kernel(cmd):
    # Install the kernel spec when we install the package
    from ipykernel import kernelspec
    from jupyter_client.kernelspec import KernelSpecManager

    kernel_name = 'geonotebook%i' % sys.version_info[0]

    path = os.path.join(tempfile.mkdtemp(suffix='_kernels'), kernel_name)
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
    ksm.install_kernel_spec(
        path, kernel_name=kernel_name, user=False, prefix=sys.prefix)

    shutil.rmtree(path)


# shamelessly taken from ipyleaflet: https://github.com/ellisonbg/ipyleaflet
# Copyright (c) 2014 Brian E. Granger
here = os.path.dirname(os.path.abspath(__file__))
node_root = os.path.join(here, 'js')
is_repo = os.path.exists(os.path.join(here, '.git'))

npm_path = os.pathsep.join([
    os.path.join(node_root, 'node_modules', '.bin'),
    os.environ.get('PATH', os.defpath),
])
log.set_verbosity(log.DEBUG)
log.info('setup.py entered')
log.info('$PATH=%s' % os.environ['PATH'])


def js_prerelease(command, strict=False):
    """Decorator for building minified js/css prior to another command."""
    class DecoratedCommand(command):
        def run(self):
            jsdeps = self.distribution.get_command_obj('jsdeps')
            if not is_repo and all(os.path.exists(t) for t in jsdeps.targets):
                # sdist, nothing to do
                command.run(self)
                return

            try:
                self.distribution.run_command('jsdeps')
            except Exception as e:
                missing = [t for t in jsdeps.targets if not os.path.exists(t)]
                if strict or missing:
                    log.warn('rebuilding js and css failed')
                    if missing:
                        log.error('missing files: %s' % missing)
                    raise e
                else:
                    log.warn('rebuilding js and css failed (not a problem)')
                    log.warn(str(e))
            command.run(self)
            update_package_data(self.distribution)
    return DecoratedCommand


def update_package_data(distribution):
    """Update package_data to catch changes during setup."""
    build_py = distribution.get_command_obj('build_py')
    # distribution.package_data = find_package_data()
    # re-init build_py options which load package_data
    build_py.finalize_options()


class NPM(Command):
    description = 'install package.json dependencies using npm'

    user_options = []

    node_modules = os.path.join(node_root, 'node_modules')

    targets = [
        os.path.join(here, 'geonotebook', 'static', 'index.js'),
        os.path.join(here, 'geonotebook', 'static', 'styles.css')
    ]

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def has_npm(self):
        try:
            check_call(['npm', '--version'])
            return True
        except:
            return False

    def should_run_npm_install(self):
        return self.has_npm()

    def run(self):
        has_npm = self.has_npm()
        if not has_npm:
            log.error(
                "`npm` unavailable.  If you're running this command using "
                "sudo, make sure `npm` is available to sudo"
            )

        env = os.environ.copy()
        env['PATH'] = npm_path

        if self.should_run_npm_install():
            log.info(
                "Installing build dependencies with npm.  "
                "This may take a while..."
            )
            check_call(
                ['npm', 'install'],
                cwd=node_root, stdout=sys.stdout, stderr=sys.stderr
            )
            log.info(
                "Building static assets.  "
            )
            check_call(
                ['npm', 'run', 'build'],
                cwd=node_root, stdout=sys.stdout, stderr=sys.stderr
            )
            os.utime(self.node_modules, None)

        for t in self.targets:
            if not os.path.exists(t):
                msg = 'Missing file: %s' % t
                if not has_npm:
                    msg += '\nnpm is required to build a development version'
                raise ValueError(msg)

        # update package data in case this created new files
        update_package_data(self.distribution)


def install_geonotebook_ini(cmd):

    # cmd.dist is a pkg_resources.Distribution class, See:
    # http://setuptools.readthedocs.io/en/latest/pkg_resources.html#distribution-objects

    # pkg_resources.Distribution.location can be a lot of things,  but in the
    # case of a develop install it will be the path to the source tree. This
    # will not work if applied to more exotic install targets
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

                log.info("copying {} to {}".format(src, dest))

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
        'develop': CustomDevelop,
        'build_py': js_prerelease(build_py),
        'egg_info': js_prerelease(egg_info),
        'sdist': js_prerelease(sdist, strict=True),
        'jsdeps': NPM
    },
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    data_files=[
        ('etc', ['config/geonotebook.ini'])
    ],
    package_data={'geonotebook': ['static/*.js',
                                  'static/*.css',
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
