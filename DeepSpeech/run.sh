#!/bin/sh

set -xe

export PATH=$(dirname "$0"):$PATH

env

checks.sh

export TMP=/mnt/tmp
export TEMP=/mnt/tmp

$HOME/run_${MODEL_LANGUAGE}.sh

$HOME/package.sh
