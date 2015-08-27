#!/bin/sh

docs="
https://zenodo.org/record/10415/export/dcite3
"

for doc in $docs ; do
    file=`echo $doc | sed -e 's-^https://--' -e 's:/:_:g'`
    curl -s -o "stubdata/input/$file" "$doc"
done
