#!/usr/bin/env bash
set -xe

pushd $HOME/ds/
	if [ "${ENGLISH_COMPATIBLE}" = "1" ]; then
		IMPORT_AS_ENGLISH="--normalize"
	fi;

	if [ ! -f "/mnt/extracted/data/M-AILABS/it_IT/it_IT_train.csv" ]; then
		# added --skiplist nothing to avoid issues with the importer TODO: find a proper solution
		python bin/import_m-ailabs.py ${IMPORT_AS_ENGLISH} \
		    --skiplist nothing\
			--language it_IT                                \
			/mnt/extracted/data/M-AILABS/
	fi;
popd