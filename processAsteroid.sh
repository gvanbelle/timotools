#!/bin/bash

mkdir "$1"
#find . -type f -name "*$1*" | xargs mv -t "$1/"
ls *$1*.fits | xargs mv -t "$1/"
cd $1
pp_run *.fits
cd ..
