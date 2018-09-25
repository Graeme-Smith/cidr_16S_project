#!/bin/bash

main() {
    set -ex -o pipefail
    # dx-download-all-inputs --parallel
    if [ -n "$infile" ]; then
        dx cat "$infile" > /dev/null
    fi

    mkdir -p out/outfile
    echo "Hello, world!" > out/outfile/hello-world.txt

    # dx-upload-all-outputs --parallel
    outfile=$(cat out/outfile/hello-world.txt | dx upload --destination "hello-world.txt" --brief -)
    dx-jobutil-add-output outfile "$outfile" --class=file
}

