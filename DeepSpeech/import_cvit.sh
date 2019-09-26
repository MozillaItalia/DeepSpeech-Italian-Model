#!/bin/bash

set -xe

pushd $HOME/ds/
	if [ ! -f "/mnt/sources/it.tar.gz" ]; then
		echo "Download in progress of Common Voice Italian Dataset"
		wget https://voice-prod-bundler-ee1969a6ce8178826482b88e843c335139bd3fb4.s3.amazonaws.com/cv-corpus-3/it.tar.gz -O /mnt/sources/it.tar.gz
	fi;

	sha1=$(sha1sum --binary /mnt/sources/it.tar.gz | awk '{ print $1 }')

	if [ "${sha1}" != "5df46c977b3689a080a799254a57a736fc3fc041" ]; then
		echo "Invalid Common Voice IT dataset"
		exit 1
	fi;

	if [ "${ENGLISH_COMPATIBLE}" = "1" ]; then
		IMPORT_AS_ENGLISH="--normalize"
	fi;

	if [ ! -f "/mnt/extracted/data/cv-it/clips/train.csv" ]; then
		mkdir -p /mnt/extracted/data/cv-it/ || true

		tar -C /mnt/extracted/data/cv-it/ -xf /mnt/sources/it.tar.gz

		python bin/import_cv2.py ${IMPORT_AS_ENGLISH} /mnt/extracted/data/cv-it/
	fi;
popd
