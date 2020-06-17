#!/bin/bash

set -xe

pushd $HOME/ds/
	all_train_csv="$(find /mnt/extracted/data/ -type f -name '*train.csv' -printf '%p,' | sed -e 's/,$//g')"
	all_dev_csv="$(find /mnt/extracted/data/ -type f -name '*dev.csv' -printf '%p,' | sed -e 's/,$//g')"
	all_test_csv="$(find /mnt/extracted/data/ -type f -name '*test.csv' -printf '%p,' | sed -e 's/,$//g')"

	mkdir -p /mnt/sources/feature_cache || true

        # Do not overwrite checkpoint file if model already exist: we will likely
	# only package
	# TODO: no TRANSFER_CHECKPOINT env set . Manage transfer learning
	if [ -f "/transfer-checkpoint/checkpoint" -a ! -f "/mnt/models/output_graph.pb" ]; then
		echo "Using checkpoint from ${TRANSFER_CHECKPOINT}"
		cp -a /transfer-checkpoint/* /mnt/checkpoints/
	fi;

	# Assume that if we have best_dev_checkpoint then we have trained correctly
	if [ ! -f "/mnt/checkpoints/best_dev_checkpoint" ]; then
		EARLY_STOP_FLAG="--early_stop"
		if [ "${EARLY_STOP}" = "0" ]; then
			EARLY_STOP_FLAG="--noearly_stop"
		fi;

		AMP_FLAG=""
		if [ "${AMP}" = "1" ]; then
			AMP_FLAG="--automatic_mixed_precision True"
		fi;

		python -u DeepSpeech.py \
			--show_progressbar True \
			--train_cudnn True \
			${AMP_FLAG} \
			--alphabet_config_path /mnt/models/alphabet.txt \
			--scorer /mnt/lm/kenlm.scorer \
			--feature_cache /mnt/sources/feature_cache \
			--train_files ${all_train_csv} \
			--dev_files ${all_dev_csv} \
			--test_files ${all_test_csv} \
			--train_batch_size ${BATCH_SIZE} \
			--dev_batch_size ${BATCH_SIZE} \
			--test_batch_size ${BATCH_SIZE} \
			--n_hidden ${N_HIDDEN} \
			--epochs ${EPOCHS} \
			--learning_rate ${LEARNING_RATE} \
			--dropout_rate ${DROPOUT} \
			${EARLY_STOP_FLAG} \
			--checkpoint_dir /mnt/checkpoints/
	fi;

	if [ ! -f "/mnt/models/output_graph.pb" ]; then
		python -u DeepSpeech.py \
			--alphabet_config_path /mnt/models/alphabet.txt  \
			--scorer /mnt/lm/kenlm.scorer \
			--feature_cache /mnt/sources/feature_cache \
			--n_hidden ${N_HIDDEN} \
			--load_evaluate "best" \
			--checkpoint_dir /mnt/checkpoints/ \
			--export_dir /mnt/models/ \
			--export_language "it"
	fi;

	if [ ! -f "/mnt/models/output_graph.tflite" ]; then
		python -u DeepSpeech.py \
			--alphabet_config_path /mnt/models/alphabet.txt  \
			--scorer /mnt/lm/kenlm.scorer \
			--feature_cache /mnt/sources/feature_cache \
			--n_hidden ${N_HIDDEN} \
			--load_evaluate "best" \
			--checkpoint_dir /mnt/checkpoints/ \
			--export_dir /mnt/models/ \
			--export_tflite \
			--export_language "it"
	fi;

	if [ ! -f "/mnt/models/it-it.zip" ]; then
		mkdir -p /mnt/models/it-it || rm /mnt/models/it-it/*
		python -u DeepSpeech.py \
			--alphabet_config_path /mnt/models/alphabet.txt \
			--scorer /mnt/lm/kenlm.scorer \
			--feature_cache /mnt/sources/feature_cache \
			--n_hidden ${N_HIDDEN} \
			--load_evaluate "best" \
			--checkpoint_dir /mnt/checkpoints/ \
			--export_dir /mnt/models/it-it \
			--export_zip \
			--export_language "Italiano (IT)"
	fi;

	if [ ! -f "/mnt/models/output_graph.pbmm" ]; then
		./convert_graphdef_memmapped_format --in_graph=/mnt/models/output_graph.pb --out_graph=/mnt/models/output_graph.pbmm
	fi;
popd
