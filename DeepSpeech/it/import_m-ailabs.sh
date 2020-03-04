#!/bin/bash

set -xe

pushd $HOME/ds/
	if [ "${ENGLISH_COMPATIBLE}" = "1" ]; then
		IMPORT_AS_ENGLISH="--normalize"
	fi;

	if [ ! -f "/mnt/extracted/data/M-AILABS/it_IT/it_IT_train.csv" ]; then
		python bin/import_m-ailabs.py ${IMPORT_AS_ENGLISH} \
			--filter_alphabet /mnt/models/alphabet.txt \
			--language it_IT                           \
			/mnt/extracted/data/M-AILABS/
	fi;
popd
