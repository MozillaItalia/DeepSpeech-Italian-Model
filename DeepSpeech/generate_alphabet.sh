#!/bin/bash

set -xe

pushd $HOME/ds/
	all_train_csv="$(find /mnt/extracted/data/ -type f -name '*train.csv' -printf '%p,' | sed -e 's/,$//g')"
	all_dev_csv="$(find /mnt/extracted/data/ -type f -name '*dev.csv' -printf '%p,' | sed -e 's/,$//g')"
	all_test_csv="$(find /mnt/extracted/data/ -type f -name '*test.csv' -printf '%p,' | sed -e 's/,$//g')"
	
	#replace '#' with '' in the whole dataset due to an error in sentence validator that allowed this char
	sed -i 's/#//g' /mnt/extracted/data/cv-it/clips/*test.csv
	sed -i 's/#//g' /mnt/extracted/data/cv-it/clips/*train.csv
	sed -i 's/#//g' /mnt/extracted/data/cv-it/clips/*dev.csv

	sed -i 's/…//g' /mnt/extracted/data/cv-it/clips/*test.csv
	sed -i 's/…//g' /mnt/extracted/data/cv-it/clips/*train.csv
	sed -i 's/…//g' /mnt/extracted/data/cv-it/clips/*dev.csv

	sed -i 's/µ/micro/g' /mnt/extracted/data/cv-it/clips/*test.csv
	sed -i 's/µ/micro/g' /mnt/extracted/data/cv-it/clips/*train.csv
	sed -i 's/µ/micro/g' /mnt/extracted/data/cv-it/clips/*dev.csv

	if [ ! -f "/mnt/models/alphabet.txt" ]; then
		if [ "${ENGLISH_COMPATIBLE}" = "1" ]; then
			cp data/alphabet.txt /mnt/models/alphabet.txt
		else
			python util/check_characters.py \
				--csv-files ${all_train_csv},${all_dev_csv},${all_test_csv} \
				--alphabet-format | grep -v '^#' | sort -n > /mnt/models/alphabet.txt
		fi;
	fi;
popd
