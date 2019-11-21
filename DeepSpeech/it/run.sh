#!/bin/sh

set -xe

${MODEL_LANGUAGE}/import_cvit.sh

${MODEL_LANGUAGE}/import_m-ailabs.sh

generate_alphabet.sh

${MODEL_LANGUAGE}/build_lm.sh

${MODEL_LANGUAGE}/train.sh

${MODEL_LANGUAGE}/evaluate_lm.sh
