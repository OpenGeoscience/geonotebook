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
         python2 \
         python2-pip \
         python2-cffi \
         python2-lxml \
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
         mapnik


RUN set -ex \
    && pip2 install \
         notebook \
         mapnik \
         scikit-image

# Generate default config and disable authentication
RUN /usr/sbin/jupyter-notebook --generate-config \
    && sed -i s/#c.NotebookApp.token\ \=\ \'\'/c.NotebookApp.token\ \=\ \'\'/g \
           /root/.jupyter/jupyter_notebook_config.py

VOLUME /notebooks
WORKDIR /notebooks
ADD jupyter.sh /jupyter.sh
