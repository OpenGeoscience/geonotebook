FROM andrewosh/binder-base

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

RUN pip2.7 install notebook \
                   mapnik \
                   pyproj \
                   ipywidgets \
                   scikit-image

RUN jupyter nbextension enable --py widgetsnbextension --sys-prefix

# Generate default config and disable authentication



RUN pip2.7 install https://github.com/OpenGeoscience/KTile/archive/master.zip

RUN apt-get install -y python-openssl python-cffi libffi-dev libssl-dev

ADD . /opt/geonotebook
ADD devops/docker/jupyter.sh /jupyter.sh

WORKDIR /opt/geonotebook

RUN pip2.7 install -r prerequirements.txt && \
    pip2.7 install -r requirements.txt && \
    pip2.7 install . && \
    jupyter serverextension enable --py geonotebook --sys-prefix && \
    jupyter nbextension enable --py geonotebook --sys-prefix

VOLUME /notebooks
WORKDIR /notebooks
CMD  ../jupyter.sh
