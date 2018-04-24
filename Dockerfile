FROM ubuntu:16.04

RUN apt-get update -y && apt-get upgrade -y
RUN apt-get install -y gcc g++ make curl

RUN apt-get install -y libgeos-dev

RUN curl -O http://download.osgeo.org/gdal/2.1.3/gdal-2.1.3.tar.gz
RUN tar -xzf gdal-2.1.3.tar.gz

WORKDIR gdal-2.1.3

RUN ./configure
RUN make -j$(nproc)
RUN make install
RUN ldconfig

RUN apt-get install -y git \
                       ssh \
                       libffi-dev \
                       libssl-dev \
                       libproj-dev \
                       python-pip \
                       python-cffi \
                       python-lxml \
                       python-pil \
                       python-numpy \
                       python-scipy \
                       python-pandas \
                       python-matplotlib \
                       python-seaborn \
                       python-concurrent.futures \
                       cython \
                       python-scikits-learn \
                       python-scikits.statsmodels \
                       python-skimage-lib

# Generates pip2.7
RUN pip install -U pip

RUN pip2.7 install -U jupyter notebook \
                   mapnik \
                   pyproj \
                   ipywidgets \
                   scikit-image \
                   pyOpenSSL

RUN jupyter nbextension enable --py widgetsnbextension --sys-prefix

# Generate default config and disable authentication
RUN jupyter-notebook --generate-config --allow-root
RUN sed -i "s/#c.NotebookApp.token = '<generated>'/c.NotebookApp.token = ''/" /root/.jupyter/jupyter_notebook_config.py

# Install/setup NVM
RUN curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.33.1/install.sh | bash \
    && . /root/.bashrc && nvm install v6.10.1 && ln -s /root/.nvm/versions/node/v6.10.1/bin/npm /usr/bin/npm

RUN pip2.7 install https://github.com/OpenGeoscience/KTile/archive/master.zip


ADD . /opt/geonotebook
ADD ./devops/docker/jupyter.sh /jupyter.sh

WORKDIR /opt/geonotebook

RUN .  /root/.bashrc && pip2.7 install -U -r prerequirements.txt && \
    pip2.7 install -U -r requirements.txt . && \
    jupyter serverextension enable --py geonotebook --sys-prefix && \
    jupyter nbextension enable --py geonotebook --sys-prefix

VOLUME /notebooks
WORKDIR /notebooks

ENTRYPOINT ["/jupyter.sh"]
