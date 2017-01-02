#/bin/bash

GIRDER_DATA_URL=https://data.kitware.com/api/v1/folder/586a75798d777f1e3428d829/download

TMPFILE=`mktemp`

wget $GIRDER_DATA_URL -O $TMPFILE
unzip -d `pwd` $TMPFILE
rm $TMPFILE
