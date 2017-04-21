FROM ubuntu:16.04

# System requirements
RUN apt-get update -y && apt-get upgrade -y
                       # Base dependencies
RUN apt-get install -y gcc \
                       g++ \
                       make \
                       curl \
                       unzip \
                       wget \
                       git \
                       pkg-config \
                       # Python/python-mapnik dependencies
                       libffi-dev \
                       libssl-dev \
                       python-dev \
                       python3-dev \
                       python3-setuptools \
                       python3-wheel \
                       python3-pip \
                       # GDAL dependencies
                       libgeos-dev \
                       # Mapnik dependencies
                       libboost-python1.58-dev \
                       libboost-filesystem1.58-dev \
                       libboost-program-options1.58-dev \
                       libboost-regex1.58-dev \
                       libboost-system1.58-dev \
                       libboost-thread1.58-dev \
                       libcairo-dev \
                       libcurl4-gnutls-dev \
                       libfreetype6-dev \
                       libharfbuzz-dev \
                       libicu-dev \
                       libjpeg-dev \
                       libpng-dev \
                       libpq-dev \
                       libproj-dev \
                       libsqlite3-dev \
                       libtiff-dev \
                       libtool \
                       libwebp-dev \
                       libxml2-dev \
                       zlib1g-dev \
                       libsqlite3-dev \
                       libproj-dev \
                       libjpeg-dev \
                       libtiff5-dev

# Python requirements
RUN pip3 install -U pip tox

# Source for mapnik, python-mapnik & GDAL
RUN cd /root && \
    git clone -b v3.0.13 --recursive https://github.com/mapnik/mapnik.git && \
    git clone -b v3.0.13 --recursive https://github.com/mapnik/python-mapnik.git && \
    curl -O http://download.osgeo.org/gdal/2.1.3/gdal-2.1.3.tar.gz && \
    tar -xzf gdal-2.1.3.tar.gz


# Install GDAL
# TODO:  configure here needs to be set up with more sophisticated
#        options like --with-hdf4 --with-netcdf, etc. This will also
#        require system libraries etc be installed
RUN cd /root/gdal-2.1.3 && ./configure && make -j$(nproc) && make install && ldconfig

# Install Mapnik
RUN cd /root/mapnik && \
    JOBS=$(nproc) python scons/scons.py PYTHON=/usr/bin/python3 BOOST_PYTHON_LIB=boost_python35 && \
    python scons/scons.py install

# Build python-mapnik wheel, make it available to tox
RUN cd /root/python-mapnik && \
    python3 setup.py bdist_wheel && \
    mkdir -p /root/.tox/distshare && \
    ln -s /root/python-mapnik/dist/*.whl /root/.tox/distshare/

# Install python-mapnik
# Note: This should not be nessisary,  except setup.py
#       won't run AT ALL if python-mapnik isn't installed
RUN pip install /root/python-mapnik/dist/*.whl

# Install nvm,  and nodejs v6
RUN curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.33.1/install.sh | bash \
    && . /root/.bashrc && nvm install v6.10.1 && ln -s /root/.nvm/versions/node/v6.10.1/bin/npm /usr/bin/npm

WORKDIR /root

CMD ["/bin/bash"]
