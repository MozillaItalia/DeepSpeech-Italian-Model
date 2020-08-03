#!/bin/bash

set -xe

pushd $DS_DIR

  if [ ! -f "/mnt/extracted/data/cv-it_tiny/train.csv" ]; then
		mkdir -p /mnt/extracted/data/cv-it_tiny/ || true

    wget -O - https://github.com/MozillaItalia/DeepSpeech-Italian-Model/files/4610711/cv-it_tiny.tar.gz | \
    tar -zxv -C /mnt/extracted/data/cv-it_tiny/
  fi
