## GeoNotebook [![CircleCI](https://circleci.com/gh/OpenGeoscience/geonotebook.svg?style=shield)](https://circleci.com/gh/OpenGeoscience/geonotebook) [![Gitter chat](https://badges.gitter.im/gitterHQ/gitter.png)](https://gitter.im/OpenGeoscience/geonotebook)
GeoNotebook is an application that provides client/server
environment with interactive visualization and analysis capabilities
using [Jupyter](http://jupyter.org), [GeoJS](http://www.github.com/OpenGeoscience/geojs) and other open source tools.
Jointly developed by  [Kitware](http://www.kitware.com) and
[NASA Ames](https://www.nasa.gov/centers/ames/home/index.html).

Documentation for GeoNotebook can be found at http://geonotebook.readthedocs.io.

## Screenshots
![screen shot](https://data.kitware.com/api/v1/file/5898b1788d777f07219fcafb/download?contentDisposition=inline)

Checkout some additional [screenshots](screenshots/)


## Installation

### System Prerequisites

For default tile serving
  + GDAL >= 2.1.0
  + mapnik >= 3.1.0
  + python-mapnik >= 0.1

### Clone the repo:
```bash
git clone https://github.com/OpenGeoscience/geonotebook.git
cd geonotebook
```
### Make a virtualenv, install jupyter[notebook], install geonotebook
```bash
mkvirtualenv -a . geonotebook

# Numpy must be fully installed before rasterio
pip install -r prerequirements.txt

pip install -r requirements.txt

pip install .

# Enable both the notebook and server extensions
jupyter serverextension enable --sys-prefix --py geonotebook
jupyter nbextension enable --sys-prefix --py geonotebook
```

*Note* The `serverextension` and `nbextension` commands accept flags that configure how
and where the extensions are installed.  See `jupyter serverextension --help` for more
information.

### Installing geonotebook for development
When developing geonotebook, it is often helpful to install packages as a reference to the
checked out repository rather than copying them to the system `site-packages`.  A "development
install" will allow you to make live changes to python or javascript without reinstalling the
package.
```bash
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
```

### Run the notebook:
```bash
cd notebooks/
jupyter notebook
```

### Configure the notebook:
Geonotebook relies on a configuration for several of its options. The system will merge configuration files in the following precedence:

+ /etc/geonotebook.ini
+ /usr/etc/geonotebook.ini
+ /usr/local/etc/geonotebook.ini
+ ```sys.prefix```/etc/geonotebook.ini 
  (e.g. /home/user/.virtual_environments/geonotebook/etc/geonotebook.inig)
+ ~/.geonotebook.ini
+ ```os.getcwd()```/.geonotebook.ini
+ any path specified in the ```GEONOTEBOOK_INI``` environment variable.

The [default configuration](config/geonotebook.ini) is installed in ```sys.prefix```/etc/geonotebook.ini


### Run the tests
```bash
# From the source root
pip install -r requirements-dev.txt
tox

# Optionally only run tests on python 2.7
# tox -e py27
```

## Docker Container
System requirements for running the notebook can sometimes prove burdensome to install. To ease these issues we have included a [docker container](devops/docker) that will run the notebook inside a containerized process. 

## Vagrant Machine
Additionally there is a `Vagrantfile` for standing up an instance of Geonotebook within a virtual machine, further instructions can be found [here](Vagrant.md).

## Tile Server

By default geonotebook provides its own tile server based on [Mapnik](https://github.com/mapnik) and [GDAL](http://www.gdal.org/) as a Jupyter Notebook server extension. Assuming system pre-requisites are available this should not need to be configured. Alternately geonotebook may be configured to use a pre-existing [Geoserver](http://geoserver.org/) for serving tiles. A built in geoserver implementation is available as a virtual machine in devops/geoserver/.  

### Use geoserver for tile serving
First provision the geoserver

```
cd devops/geoserver/
vagrant up
```

Second change the ```vis_server``` configuration to ```geoserver``` in the ```[default]``` section of your configuration. Then include a ```[geoserver]``` section with the pertinent configuration.  E.g.:

```
[default]
vis_server=geoserver

...

[geoserver]
username = admin
password = geoserver
url = http://127.0.0.1:8080/geoserver
```
