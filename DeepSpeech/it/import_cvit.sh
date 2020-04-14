#!/bin/bash

set -xe

pushd $HOME/ds/
	if [ ! -f "/mnt/sources/it.tar.gz" ]; then
			echo "please download Common Voice IT dataset"
			exit 1
	fi;

	sha1=$(sha1sum --binary /mnt/sources/it.tar.gz | awk '{ print $1 }')

	if [ "${sha1}" != "5949823c7531695fefc3bcab5a56f43552eb7d89" ]; then
		echo "Invalid Common Voice IT dataset"
		exit 1
	fi;

	if [ "${ENGLISH_COMPATIBLE}" = "1" ]; then
		IMPORT_AS_ENGLISH="--normalize"
	fi;

	if [ ! -f "/mnt/extracted/data/cv-it/clips/train.csv" ]; then
		mkdir -p /mnt/extracted/data/cv-it/ || true

		tar -C /mnt/extracted/data/cv-it/ -xf /mnt/sources/it.tar.gz

		python bin/import_cv2.py ${IMPORT_AS_ENGLISH} --filter_alphabet=/mnt/models/alphabet.txt /mnt/extracted/data/cv-it/
	fi;
popd
