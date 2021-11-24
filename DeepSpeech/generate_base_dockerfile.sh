#!/bin/bash
DS_SHA=f2e9c85880dff94115ab510cde9ca4af7ee51c19

rm Makefile Dockerfile.train.tmpl
wget https://github.com/mozilla/DeepSpeech/raw/$DS_SHA/Makefile
wget https://github.com/mozilla/DeepSpeech/raw/$DS_SHA/Dockerfile.train.tmpl

# install libmagic
sed -i '/libbz2-dev/a \\tlibmagic-dev \\' Dockerfile.train.tmpl

# fix swig url
sed -i "/^RUN git checkout \$DEEPSPEECH_SHA/a \
RUN sed -i 's|swig/4.0.2|swig/4.1.0|' native_client/definitions.mk\n\
RUN sed -i -E 's|community-tc.*swig(.*)amd64.*tar|github.com/mozilla/DeepSpeech/releases/download/v0.9.3/ds-swig\\\1amd64.tar|g' native_client/definitions.mk" \
Dockerfile.train.tmpl

make Dockerfile.train DEEPSPEECH_SHA=$DS_SHA

# do not execute the RUN directive
sed -i '$ d' Dockerfile.train
