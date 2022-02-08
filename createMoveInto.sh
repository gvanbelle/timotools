#!/bin/bash

mkdir "$1"
find . -type f -name "*$1*" | xargs mv -t "$1/"

