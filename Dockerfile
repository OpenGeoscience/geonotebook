FROM base/archlinux:latest

RUN set -ex \
    && pacman -Sy --noconfirm archlinux-keyring \
    && pacman -Syu --noconfirm \
    && pacman-db-upgrade \
    && pacman -S --noconfirm \
         ca-certificates \
         ca-certificates-utils

RUN set -ex \
    && pacman -S --noconfirm \
         git \
         openssh \
         npm \
         autoconf \
         automake \
         gcc \
         python2 \
         python2-pip \
         python2-cffi \
         python2-lxml \
         python2-pillow \
         python2-numpy \
         python2-scipy \
         python2-pandas \
         python2-matplotlib \
         python2-seaborn \
         python2-statsmodels \
         python2-scikit-learn \
         cython \
         python2-futures \
         gdal \
         mapnik \
         sed


RUN set -ex \
    && pip2 install \
         notebook \
         mapnik \
         pyproj \
         ipywidgets \
         scikit-image

RUN jupyter nbextension enable --py widgetsnbextension --sys-prefix

# Generate default config and disable authentication
RUN /usr/sbin/jupyter-notebook --generate-config \
    && sed -i s/#c.NotebookApp.token\ \=\ \'\'/c.NotebookApp.token\ \=\ \'\'/g \
           /root/.jupyter/jupyter_notebook_config.py

RUN pip2 install https://github.com/OpenGeoscience/KTile/archive/master.zip

ADD . /opt/geonotebook
ADD devops/docker/jupyter.sh /jupyter.sh

RUN pushd /opt/geonotebook \
    && pip2 install . \
    && jupyter serverextension enable --py geonotebook --sys-prefix \
    && jupyter nbextension enable --py geonotebook --sys-prefix

VOLUME /notebooks
WORKDIR /notebooks
CMD ../jupyter.sh
