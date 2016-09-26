## Installation
### Clone the repo:
```bash
git clone git@github.com:OpenGeoscience/geonotebook.git
cd geonotebook
```
### Make a virtualenv, install jupyter[notebook], install geonotebook
```bash
mkvirtualenv -a . geonotebook

pip install -r requirements.txt

pip install .

# Optionally you may do a development install, e.g.
# pip install -e .
```

*Note* The geonotebook package has been designed to install the notebook extension etc automatically. You should not need to run ```jupyter nbextension install ...``` etc.

### Ensure a running geoserver for tile serving
```
cd devops/geoserver/
vagrant up
```

### Run the notebook:
```bash
cd notebooks/
jupyter notebook

```

### Run the tests
```bash
# From the source root
python setup.py test
```



