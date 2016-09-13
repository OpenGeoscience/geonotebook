Clone the repo:
```bash
git clone git@github.com:OpenGeoscience/geonotebook.git
cd geonotebook
```
Make a virtualenv and install ```jupyter[notebook]``` and development install geonotebook
```bash
mkvirtualenv -a . geonotebook
pip install -r requirements.txt
pip install -e .
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
