## GeoNotebook [![CircleCI](https://circleci.com/gh/OpenGeoscience/geonotebook.svg?style=shield)](https://circleci.com/gh/OpenGeoscience/geonotebook) [![Gitter chat](https://badges.gitter.im/gitterHQ/gitter.png)](https://gitter.im/OpenGeoscience/geonotebook)
GeoNotebook is an application that provides client/server
environment with interactive visualization and analysis capabilities
using [Jupyter](http://jupyter.org), [GeoJS]
(http://www.github.com/OpenGeoscience/geojs) and other open source tools.
Jointly developed by  [Kitware](http://www.kitware.com) and
[NASA Ames](https://www.nasa.gov/centers/ames/home/index.html).


## Screenshots
![screen shot](screenshots/geonotebook.png)

Checkout some additional [screenshots](screenshots/)


## Installation

### System Prerequisites

For default tile serving
  + GDAL >= 2.1.0
  + mapnik >= 3.1.0
  + python-mapnik >= 0.1

### Clone the repo:
```bash
git clone git@github.com:OpenGeoscience/geonotebook.git
cd geonotebook
```
### Make a virtualenv, install jupyter[notebook], install geonotebook
```bash
mkvirtualenv -a . geonotebook

# Numpy must be fully installed before rasterio
pip install -r prerequirements.txt

pip install -r requirements.txt

pip install .

# Alternatively you may do a development install, e.g.
# pip install -e .
```

*Note* The geonotebook package has been designed to install the notebook extension etc automatically. You should not need to run ```jupyter nbextension install ...``` etc.

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
