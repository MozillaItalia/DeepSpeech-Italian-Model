#!/bin/sh

set -xe

$HOME/import_cvit.sh

$HOME/generate_alphabet.sh

$HOME/build_lm.sh

$HOME/train_it.sh
