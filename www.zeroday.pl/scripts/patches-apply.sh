#!/bin/bash
#
# File: patches-apply.sh
#
# Description: Apply patches.

##
## includes
##

source $(dirname $(readlink -f $0))/includes.sh

##
## variables
##

CURRENT_DIR=$(pwd)

##
## main
##

cd $PROJECT_DIR

#patch -p1 -i ./patches/drupal-includes-database.patch # this seems to be fixed in 7.14
patch -p1 -i ./patches/drupal-modules-rules.patch
patch -p1 -i ./patches/drupal-modules-taxonomy.patch

cd $CURRENT_DIR

exit 0
