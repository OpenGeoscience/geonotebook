Installation & Configuration
============================

.. toctree::
   :maxdepth: 2


Prerequisites (for default tile serving)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
- GDAL >= 2.1.0
- mapnik >= 3.1.0
- python-mapnik >= 0.1


Basic Install
^^^^^^^^^^^^^

.. code-block:: bash

    git clone https://github.com/OpenGeoscience/geonotebook.git
    cd geonotebook

    ### Make a virtualenv, install jupyter[notebook], install geonotebook
    mkvirtualenv -a . geonotebook

    # Numpy must be fully installed before rasterio
    pip install -r prerequirements.txt

    pip install -r requirements.txt

    pip install .

    # Enable both the notebook and server extensions
    jupyter serverextension enable --sys-prefix --py geonotebook
    jupyter nbextension enable --sys-prefix --py geonotebook

.. note:: The ``serverextension`` and ``nbextension`` commands accept flags that configure how
          and where the extensions are installed.  See ``jupyter serverextension --help`` for more
          information.



Development Install
^^^^^^^^^^^^^^^^^^^
When developing GeoNotebook, it is often helpful to install packages as a reference to the
checked out repository rather than copying them to the system `site-packages`.  A "development
install" will allow you to make live changes to python or javascript without reinstalling the
package.

.. code-block:: bash

    # Install the geonotebook python package as "editable"
    pip install -e .

    # Install the notebook extension as a symlink
    jupyter nbextension install --sys-prefix --symlink --py geonotebook

    # Enable the extension
    jupyter serverextension enable --sys-prefix --py geonotebook
    jupyter nbextension enable --sys-prefix --py geonotebook

    # Start the javascript builder
    cd js
    npm run watch


Vagrant Install
^^^^^^^^^^^^^^^

.. code-block:: bash

    # Start and provision virtual machine
    vagrant up

    # See GeoNotebook is running at http://localhost:8888


Configurable Options
$$$$$$$$$$$$$$$$$$$$


+----------------------------+--------------------------------------------------------+
| variable                   | comments                                               |
+============================+========================================================+
| VAGRANT\_MEMORY            | The number (in MB) of RAM to use on the virtual        |
|                            | machine (defaults to 2048).                            |
+----------------------------+--------------------------------------------------------+
| VAGRANT\_CPUS              | The number of CPUs to use on the virtual machine       |
|                            | (defaults to 2).                                       |
+----------------------------+--------------------------------------------------------+
| GEONOTEBOOK\_DIR           | Documentation for this can be found in the             |
|                            | `GeoNotebook role docs`_.                              |
+----------------------------+--------------------------------------------------------+
| GEONOTEBOOK\_VERSION       | Documentation for this can be found in the             |
|                            | `GeoNotebook role docs`_.                              |
+----------------------------+--------------------------------------------------------+
| GEONOTEBOOK\_UPDATE        | Documentation for this can be found in the             |
|                            | `GeoNotebook role docs`_.                              |
+----------------------------+--------------------------------------------------------+
| GEONOTEBOOK\_FORCE         | Documentation for this can be found in the             |
|                            | `GeoNotebook role docs`_.                              |
+----------------------------+--------------------------------------------------------+
| GEONOTEBOOK\_AUTH\_ENABLED | Documentation for this can be found in the             |
|                            | `GeoNotebook role docs`_.                              |
+----------------------------+--------------------------------------------------------+
| GEONOTEBOOK\_AUTH\_TOKEN   | Documentation for this can be found in the             |
|                            | `GeoNotebook role docs`_.                              |
+----------------------------+--------------------------------------------------------+

.. _GeoNotebook role docs: devops/roles/geonotebook

.. warning:: By default, Jupyter authentication is disabled in the Vagrant environment as it's meant to be a development environment. Jupyter authentication should always be enabled on production systems.

         If Jupyter authentication is desired, the environment variables related to ``GEONOTEBOOK_AUTH_*`` must be set, note the auth token must be set to the same token each time the machine is provisioned.


Docker Install
^^^^^^^^^^^^^^
GeoNotebook relies on a complex stack of technologies that are not always easy to install and properly configure. To ease this complexity we provide a docker container for running the notebook on docker compatible systems. To install docker on your system please see Docker's `documentation <https://docs.docker.com/engine/installation/>`_ for your operating system.

First you must build the docker container.  After checking out the current repository, you can run ::

    docker build -t geonotebook .


This will build and install the container on your system,  making it available to run. This may take some time (between 10 and 20 minutes) depending on your network connection.


To run the container (after building it)  issue the following command: ::

    docker run -p 8888:8888 -v /path/to/your/notebooks:/notebooks  -it --rm geonotebook

This does several things.

**First** it maps the docker container's ``8888`` port to your system's ``8888`` port.  This makes the container available to your host systems web browser.

**Second**,  it maps a host system path ``/path/to/your/notebooks`` to the docker containers ``/notebooks`` directory.  This ensures that the notebooks you create, edit, and save are available on your host system,  and are not *destroyed* when the you exit the container.

**Third**, the notebook starts in an interactive terminal and is accessible through http://localhost:8888.

**Finally**,  we include the ``--rm`` option to clean up the notebook after you exit the process.

.. note:: You actually *can* run the docker container without the ``-it`` option and still get access to the initial URL (though this is somewhat more complicated). It is possible to get the notebook's container name (e.g. with ``docker ps``) and then print the output of the container with ``docker logs [OPTIONS] CONTAINER``  For more information see ``docker logs --help``

.. note:: You may want to keep your data separate from your notebook files.  If this is the case you can map
   additional directories from your host into the docker container using the -v option.  E.g. ::

       docker run -p 8888:8888 -v /path/to/your/notebooks:/notebooks \
       -v /path/to/your/data:/data -it --rm geonotebook

Configuring
^^^^^^^^^^^
GeoNotebook relies on a configuration for several of its options. The system will merge configuration files in the following precedence:

- /etc/geonotebook.ini
- /usr/etc/geonotebook.ini
- /usr/local/etc/geonotebook.ini
- ``sys.prefix``/etc/geonotebook.ini (e.g. /home/user/.virtual_environments/geonotebook/etc/geonotebook.ini)
- ~/.geonotebook.ini
- ``os.getcwd()``/.geonotebook.ini
- any path specified in the ``GEONOTEBOOK_INI`` environment variable.

The  `default configuration <https://github.com/OpenGeoscience/geonotebook/blob/master/config/geonotebook.ini>`_ is installed in ``sys.prefix``/etc/geonotebook.ini.

.. seealso:: Verifying the functionality of GeoNotebook is detailed in the :ref:`automated-testing` section.
