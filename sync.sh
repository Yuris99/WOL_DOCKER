#!/bin/bash

LOCAL_PATH="/mnt/c/Users/mose1/Documents/Projects/wol_docker/WOL_DOCKER/"
NAS_PATH="/mnt/w/WOL_DOCKER/"

inotifywait -m -r -e modify,attrib,close_write,move,create,delete $LOCAL_PATH |
while read -r directory events filename; do
    rsync -av --delete $LOCAL_PATH $NAS_PATH
done
