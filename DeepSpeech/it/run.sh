#!/bin/sh

set -xe

generate_alphabet.sh

if [ "${FAST_TRAIN}" = 1 ]; then
  ${MODEL_LANGUAGE}/import_cvit_tiny.sh
  export BATCH_SIZE=2
else
  ${MODEL_LANGUAGE}/import_voxforge.sh
  ${MODEL_LANGUAGE}/import_cvit.sh
  ${MODEL_LANGUAGE}/import_m-ailabs.sh
fi

${MODEL_LANGUAGE}/build_lm.sh
if [ "${ONLY_EXPORT}" = 0 ]; then
  ${MODEL_LANGUAGE}/train.sh
fi;

${MODEL_LANGUAGE}/export.sh

${MODEL_LANGUAGE}/evaluate_lm.sh
