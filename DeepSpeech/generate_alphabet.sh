#!/bin/bash

set -xe

pushd $DS_DIR
	if [ ! -f "/mnt/models/alphabet.txt" ]; then
		if [ "${ENGLISH_COMPATIBLE}" = "1" ]; then
			cp data/alphabet.txt /mnt/models/alphabet.txt
		else
			cp $HOME/italian_alphabet.txt /mnt/models/alphabet.txt
		fi;
	fi;
popd
