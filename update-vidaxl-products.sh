#!/bin/bash
# update-vidaxl-products.sh
echo $0

FULL_PATH=$(realpath $0)
# echo $FULL_PATH
DIR_PATH=$(dirname $FULL_PATH)
# echo $DIR_PATH
cd $DIR_PATH
source .venv/bin/activate
# flask update-vidaxl-products --count 1000 2>&1 | tee -a /tmp/update-vidaxl-products.log
flask update-vidaxl-products 2>&1 | tee -a /tmp/update-vidaxl-products.log
