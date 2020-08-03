#!/bin/bash

set -xe

pushd $DS_DIR
	if [ ! -f "/mnt/sources/it.tar.gz" ]; then
			echo "please download Common Voice IT dataset"
			exit 1
	fi;

	if [ ! -f "/mnt/extracted/data/cv-it/clips/train.csv" ]; then
        if ! echo "a304332d1dfdb772ae75859441f46a88438305d2f5420680c3c64fba62ea6830  /mnt/sources/it.tar.gz" | sha256sum --check; then
            echo "Invalid Common Voice IT dataset"
            exit 1
        fi;

        if [ "${ENGLISH_COMPATIBLE}" = "1" ]; then
            IMPORT_AS_ENGLISH="--normalize"
        fi;

		mkdir -p /mnt/extracted/data/cv-it/ || true

		tar -C /mnt/extracted/data/cv-it/ --strip-components=2 -xf /mnt/sources/it.tar.gz

		if [ ${DUPLICATE_SENTENCE_COUNT} -gt 1 ]; then

			create-corpora -d /mnt/extracted/corpora -f /mnt/extracted/data/cv-it/validated.tsv -l it -s ${DUPLICATE_SENTENCE_COUNT}

			mv /mnt/extracted/corpora/it/*.tsv /mnt/extracted/data/cv-it/

		fi;

		python bin/import_cv2.py ${IMPORT_AS_ENGLISH} --filter_alphabet=/mnt/models/alphabet.txt /mnt/extracted/data/cv-it/
	fi;
popd
