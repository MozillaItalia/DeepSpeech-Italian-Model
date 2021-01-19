Model Training Steps
=================
*Read this in other languages: [Italian](README.it-IT.md)*
</br>

Once the Docker container is started, the scripts that are executed are, in order:

| SCRIPT   |  |
| -------------  | ------------- |
| `../check.sh` | Runs a simple check to make sure all necessary directories have been created and starts two iterations on a mini dataset |
| `../generate_alphabet.sh` | if the file `/mnt/models/alphabet.txt` is not present, it is taken and copied from `~/data` |
| `import_cvit_tiny.sh` | import the test dataset `cv_tiny` if the flag `FAST_TRAIN` is set equal to `1` otherwise it is skipped |
| `import_cvit.sh` | import the italian CommonVoice dataset unpacking it from `/mnt/sources/en.tar.gz` |
| `import_m-ailabs.sh` | download and import M-AILABS Italian dataset |
| `build_lm.sh` | download the corpora `mitads.txt` if not present and start the creation of the package scorer `scorer` after creating the file `lm.binary` and `vocab-500000.txt` | |
| `train.sh` | starts the actual training **only after user confirmation**. If the flag `TRANSFER_LEARNING=1` is present the English release checkpoint is downloaded, the flag `DROP_SOURCE_LAYERS=1` is added and the weights of all layers but not the last one (the network output layer) are used.
| `export.sh` | Checks the `/mnt/models` directory and, if not present, generates model binaries for: Tensorflow, TFLite, zipper containing TFLite model and scorer, Tensorflow model memory mapped|.
| `evaluate_lm.sh` | if `LM_EVALUATE_RANGE` contains a triplet of positive integers `ALPHA_MAX,BETA_MAX,N_TRIALS` the DeepSpeech script `lm_optimizer.py` is started to search within `N_TRIALS` attempts for the best value of `LM_ALPHA` and `LM_BETA` that minimize the Word Error Rate on the Validation Set. Once obtained, you will need to re-run DeepSpeech's `./generate_scorer_package` script to recreate the new scorer with the `default_alpha` and `default_beta` flags equal to the new ones obtained |
| `../package.sh` | Check the `/mnt` directory and, if not present, generate the archives: `model_tensorflow_en.tar.xz` with the memory mapped file, `scorer` and `alphabet. txt`, `model_tflite_en.tar.xz` with the TFLite model, `scorer` and `alphabet.txt`, `checkpoint_en.tar.xz` with the latest `best_dev_checkpoint_xxx`. Finally copy the files `.zip` in `/mnt/models/` to `/mnt/`.
