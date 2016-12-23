#/bin/bash

if hash aws 2>/dev/null; then
    aws s3 cp s3://golden-tile-geotiffs/L57.Globe.month02.2009.hh09vv04.h6v1.doy032to055.NBAR.v3.0.tiff WELD.tif;
else
    echo "AWS CLI script 'aws' is required"
fi
