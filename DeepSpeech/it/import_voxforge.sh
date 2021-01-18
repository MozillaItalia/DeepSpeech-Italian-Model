#!/bin/bash

set -xe

pushd $DS_DIR

	if [ ! -f "/mnt/extracted/data/voxforge/voxforge_train.csv" ]; then

		mv bin/import_voxforge.py bin/import_voxforge_bak.py
		sed 's%/SpeechCorpus/%/it/%g' bin/import_voxforge_bak.py > \
			bin/import_voxforge.py

		python bin/import_voxforge.py \
			/mnt/extracted/data/voxforge
		# uncomment if you want to delete all the tar.gz archives
		# rm -rf /mnt/extracted/data/voxforge/archive
		# del blacklisted speakers
		rm -rf /mnt/extracted/data/voxforge/train/anonymous-20080723-ouv
		rm -rf /mnt/extracted/data/voxforge/train/anonymous-20080723-ouv
		rm -rf /mnt/extracted/data/voxforge/train/anonymous-20080725-dey
		rm -rf /mnt/extracted/data/voxforge/train/Vistaus-20080718-mrm

	fi;
popd
