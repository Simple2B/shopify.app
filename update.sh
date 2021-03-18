#!/bin/bash
# update.sh
# run update ALL
echo $0

FULL_PATH=$(realpath $0)
# echo $FULL_PATH
DIR_PATH=$(dirname $FULL_PATH)
# echo $DIR_PATH
cd $DIR_PATH
source .venv/bin/activate
USER=`whoami`
flask update 2>&1 | tee -a /tmp/update-all-${USER}.log