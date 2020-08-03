#!/bin/bash
DS_SHA=f56b07dab4542eecfb72e059079db6c2603cc0ee

wget https://github.com/mozilla/DeepSpeech/raw/$DS_SHA/Makefile
wget https://github.com/mozilla/DeepSpeech/raw/$DS_SHA/Dockerfile.train.tmpl

make Dockerfile.train DEEPSPEECH_SHA=$DS_SHA

# do not execute the RUN directive
sed -i '$ d' Dockerfile.train
