## GeoNotebook
GeoNotebook is an application that provides client/server
enviroment with inteactive visualization and analysis capabilities
using [Jupyter](http://jupyter.org), [GeoJS]
(http://www.github.com/OpenGeoscience/geojs) and other open source tools.
Jointly developed by  [Kitware](http://www.kitware.com) and
[NASA Ames](https://www.nasa.gov/centers/ames/home/index.html),
GeoNotebook is designed for big data and cloud enabled data analysis
and visualization.

## Installation
Clone the repo:
```bash
git clone git@github.com:OpenGeoscience/geonotebook.git
cd geonotebook
```
Make a virtualenv and install ```jupyter[notebook]``` and development install geonotebook
```bash
mkvirtualenv -a . geonotebook
pip install -r requirements.txt
pip install .
# Optionally you may do a development install, e.g.
# pip install -e .
```

Install the serverextension and nbextenion
```bash
jupyter nbextension install --py geonotebook --sys-prefix
jupyter nbextension enable --py geonotebook --sys-prefix
jupyter serverextension enable --py geonotebook --sys-prefix
```

Run the notebook:
```bash
cd notebooks/
jupyter notebook

```

Run the tests
```bash
python setup.py test
```



