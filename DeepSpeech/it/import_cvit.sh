#!/bin/bash

set -xe

pushd $HOME/ds/
	if [ ! -f "/mnt/sources/it.tar.gz" ]; then
			echo "please download Common Voice IT dataset"
			exit 1
	fi;

	sha256=$(sha256sum --binary /mnt/sources/it.tar.gz | awk '{ print $1 }')

	if [ "sha256" != "a304332d1dfdb772ae75859441f46a88438305d2f5420680c3c64fba62ea6830" ]; then
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
