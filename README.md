Clone the repo:
```bash
git clone git@github.com:OpenGeoscience/geonotebook.git
cd geonotebook
```
Make a virtualenv and install ```jupyter[notebook]``` and development install geonotebook
```bash
mkvirtualenv -a . geonotebook
pip install "jupyter[notebook]"

pip install -e .
```

Install the serverextension and nbextenion
```bash
# Sometimes nessisary after installing new binaries (like jupyter) into virtualenv
rehash

jupyter nbextension install --py geonotebook --sys-prefix
jupyter nbextension enable --py geonotebook --sys-prefix
jupyter serverextension enable --py geonotebook --sys-prefix
```
Run the notebook:
```bash
jupyter notebook

```
