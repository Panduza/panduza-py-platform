#!/bin/bash
curdir=`pwd | xargs basename`

if [ $curdir == "panduza-py" ]; then
    docker build -t local/panduza-py-platform:latest platform
fi

if [ $curdir == "platform" ]; then
    docker build -t local/panduza-py-platform:latest .
fi
