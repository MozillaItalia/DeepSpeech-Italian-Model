#!/bin/bash

set -xe

pushd $DS_DIR
	all_train_csv="$(find /mnt/extracted/data/ -type f -name '*train.csv' -printf '%p,' | sed -e 's/,$//g')"
	all_dev_csv="$(find /mnt/extracted/data/ -type f -name '*dev.csv' -printf '%p,' | sed -e 's/,$//g')"
	all_test_csv="$(find /mnt/extracted/data/ -type f -name '*test.csv' -printf '%p,' | sed -e 's/,$//g')"

	mkdir -p /mnt/sources/feature_cache || true

	# save those params that are shared between different training (transfer or from scratch)
	params="--show_progressbar True \
		--train_cudnn True \
		--alphabet_config_path /mnt/models/alphabet.txt \
		--scorer /mnt/lm/scorer \
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
		--max_to_keep ${MAX_TO_KEEP} \
		--checkpoint_dir /mnt/checkpoints/ \
		--summary_dir /mnt/tboard_logs/"

	if [ "${TRANSFER_LEARNING}" = "1" ]; then
		params=$params" --drop_source_layers "${DROP_SOURCE_LAYERS}
		# disable automatic_mixed_precision because official DS checkpoints are not compatible
		AMP="0"
		if [ ! -f "/mnt/checkpoints/best_dev_checkpoint" ]; then
			echo "No checkpoints found. Downloading Deepspeech "${DS_RELEASE}" english checkpoints"
			wget -O eng_checkpoints.tar.gz "https://github.com/mozilla/DeepSpeech/releases/download/v${DS_RELEASE}/deepspeech-${DS_RELEASE}-checkpoint.tar.gz"
			tar -zxv -f eng_checkpoints.tar.gz --strip 1 -C /mnt/checkpoints/
			rm eng_checkpoints.tar.gz
		fi;
	fi;

	EARLY_STOP_FLAG="--early_stop"
	ES_EPOCHS_FLAG="--es_epochs "${ES_EPOCHS}
	if [ "${EARLY_STOP}" = "0" ]; then
		EARLY_STOP_FLAG="--noearly_stop"
		ES_EPOCHS_FLAG=""
	fi;
	EARLY_STUFF=${EARLY_STOP_FLAG}" "${ES_EPOCHS_FLAG}
	AMP_FLAG=""
	if [ "${AMP}" = "1" ]; then
		AMP_FLAG="--automatic_mixed_precision True"
	fi;

	params=${params}" "${EARLY_STUFF}" "${AMP_FLAG}

	echo    # (optional) move to a new line
	echo $params
	echo    # (optional) move to a new line
	read -p "Check all deepspeech params before training. Press any key to continue." -n 1 -r
	echo    # (optional) move to a new line
	# start the training phase even if there is a best_dev_checkpoint
	# TODO: another flag to skip training phase? Does it make sense?
	python DeepSpeech.py ${params}

popd
