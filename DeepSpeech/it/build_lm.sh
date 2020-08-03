#!/bin/bash

set -xe

pushd /mnt/extracted
	if [ "${ENGLISH_COMPATIBLE}" = "1" ]; then
		OLD_LANG=${LANG}
		export LANG=it_IT.UTF-8
	fi;

	if [ ! -f "mitads.txt" ]; then
		curl -sSL https://github.com/MozillaItalia/DeepSpeech-Italian-Model/releases/download/Mitads-1.0.0-alpha/mitads-1.0.0-alpha.tar.xz | tar -xJv
	fi;

	if [ "${ENGLISH_COMPATIBLE}" = "1" ]; then
		mv mitads.txt mitads_accents.txt
		# Locally force LANG= to make iconv happy and avoid errors like:
		# iconv: illegal input sequence at position 4468
		# Also required locales and locales-all to be installed
		head -n 5 mitads_accents.txt
		iconv -f UTF-8 -t ASCII//TRANSLIT//IGNORE < mitads_accents.txt > mitads.txt
		head -n 5 mitads.txt
		> mitads_accents.txt
	fi;

	if [ ! -f "/mnt/lm/scorer" ]; then
		pushd $DS_DIR/data/lm
			top_k=500000
			if [ "${FAST_TRAIN}" = 1 ]; then
				head -10000 /mnt/extracted/mitads.txt > /mnt/extracted/sources_lm.txt
				top_k=500
			else
				mv /mnt/extracted/mitads.txt /mnt/extracted/sources_lm.txt
				touch /mnt/extracted/mitads.txt
			fi

			python generate_lm.py --input_txt "/mnt/extracted/sources_lm.txt" --output_dir "/mnt/lm" \
				--top_k $top_k --kenlm_bins "$DS_DIR/native_client/kenlm/build/bin/" \
				--arpa_order 5 --max_arpa_memory "85%" --arpa_prune "0|0|1" \
				--binary_a_bits 255 --binary_q_bits 8 --binary_type trie
			if [ ! -f "generate_scorer_package" ]; then
				curl -LO https://github.com/mozilla/DeepSpeech/releases/download/v$DS_RELEASE/native_client.amd64.cuda.linux.tar.xz
				tar xvf native_client.*.tar.xz
				./generate_scorer_package --alphabet /mnt/models/alphabet.txt \
				  --lm "/mnt/lm/lm.binary" \
				  --vocab "/mnt/lm/vocab-"$top_k".txt" \
				  --package "/mnt/lm/scorer" \
				  --default_alpha 0.931289039105002 \
				  --default_beta 1.1834137581510284
			fi;
	fi;

	if [ "${ENGLISH_COMPATIBLE}" = "1" ]; then
		export LANG=${OLD_LANG}
	fi;
popd
