#!/bin/bash

set -xe

pushd $DS_DIR
	if [ ! -f "/mnt/models/output_graph.pb" ]; then
		python DeepSpeech.py \
			--alphabet_config_path /mnt/models/alphabet.txt  \
			--scorer /mnt/lm/scorer \
			--feature_cache /mnt/sources/feature_cache \
			--n_hidden ${N_HIDDEN} \
			--load_evaluate "best" \
			--checkpoint_dir /mnt/checkpoints/ \
			--export_dir /mnt/models/ \
			--export_language "it"
	fi;

	if [ ! -f "/mnt/models/output_graph.tflite" ]; then
		python DeepSpeech.py \
			--alphabet_config_path /mnt/models/alphabet.txt  \
			--scorer /mnt/lm/scorer \
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
		python DeepSpeech.py \
			--alphabet_config_path /mnt/models/alphabet.txt \
			--scorer /mnt/lm/scorer \
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
