#!/bin/sh

set -xe

generate_alphabet.sh

${MODEL_LANGUAGE}/import_cvit.sh

${MODEL_LANGUAGE}/import_m-ailabs.sh

${MODEL_LANGUAGE}/build_lm.sh

${MODEL_LANGUAGE}/train.sh

${MODEL_LANGUAGE}/evaluate_lm.sh
