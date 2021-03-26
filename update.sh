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
DATE=`date '+%Y-%m-%d'`
LOG_FILE=/tmp/update-all-${USER}-${DATE}.log
echo logfile: $LOG_FILE
echo updating...
flask update 2>&1 | tee -a $LOG_FILE
echo delete old logs...
find /tmp/update-all-${USER}* -type f -mtime +3 -exec rm -f {} \;
