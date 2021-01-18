#!/bin/bash
DS_SHA=f2e9c85880dff94115ab510cde9ca4af7ee51c19

rm Makefile
wget https://github.com/mozilla/DeepSpeech/raw/$DS_SHA/Makefile
wget https://github.com/mozilla/DeepSpeech/raw/$DS_SHA/Dockerfile.train.tmpl

make Dockerfile.train DEEPSPEECH_SHA=$DS_SHA

# do not execute the RUN directive
sed -i '$ d' Dockerfile.train
