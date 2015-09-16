#!/bin/sh

# grab the zenodo records in zenodo_records.list

cat zenodo_records.list | while read doc ; do
    record="$doc/export/dcite3"
    file=`echo "$record" | sed -e 's-^https://--' -e 's-^http://--' -e 's:/:_:g'`
    curl -s -o "stubdata/input/$file" "$record"
done
