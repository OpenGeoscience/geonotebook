#/bin/bash
set -e

dir="$(dirname $0)"

function gettemp() {
    TMPFILE=`mktemp`
}

function download() {
    gettemp
    curl $1 -o $TMPFILE
}

# tifs
download 'https://data.kitware.com/api/v1/folder/586a75798d777f1e3428d829/download'
unzip -o -d "$dir" $TMPFILE
rm $TMPFILE

# shapefile
download 'https://data.kitware.com/api/v1/item/589b390c8d777f07219fcb3e/download'
unzip -o -d "$dir/data/states_20m" $TMPFILE
rm $TMPFILE

download 'https://data.kitware.com/api/v1/file/58b96a8a8d777f0aef5d0f8c/download'
unzip -o -d "$dir/data/wa_county" $TMPFILE
rm $TMPFILE

# geojson
download 'https://data.kitware.com/api/v1/item/589b624d8d777f07219fcc60/download'
mv $TMPFILE "$dir/data/ne_50m_populated_places_simple.geojson"
