# Dockerfile for producing italian model

## Prerequistes:

* Ensure you have a running setup of `NVIDIA Docker`
* Prepare a host directory with enough space for training / producing intermediate data (100GB ?).
* Ensure it's writable by `trainer` (uid 999) user (defined in the Dockerfile).
* For Common Voice dataset, please make sure you have downloaded the dataset prior to running (behind email)
  Place `it.tar.gz` (sha1 value should be `5949823c7531695fefc3bcab5a56f43552eb7d89`) inside your host directory,
  in a `sources/` subdirectory.

## Build the image:

```
$ docker build -f Dockerfile.train.it .
```

Several parameters can be customized:
 - `ds_repo` to fetch DeepSpeech from a different repo than upstream
 - `ds_branch` to checkout a specific branch / commit
 - `ds_sha1` commit to pull from when installing pre-built binaries
 - `kenlm_repo`, `kenlm_branch` for the same parameters for KenLM
 - `english_compatible` set to 1 if you want the importers to be run in
    "English-compatible mode": this will affect behavior such as english
    alphabet file can be re-used, when doing transfer-learning from English
    checkpoints for example.
 - lm_evaluate_range, if non empty, this will perform a LM alpha/beta evaluation
    the parameter is expected to be a space-separated list of comma-separated
    "lm_alpha,lm_beta" values, e.g., "0.5,1.5 0.6,1.4"

Some parameters for the model itself:
 - `batch_size` to specify the batch size for training, dev and test dataset
 - `epoch` to specify the number of epochs to run training for
 - `learning_rate` to define the learning rate of the network
 - `dropout` to define the dropout applied
 - `lm_alpha`, `lm_beta` to control language model alpha and beta parameters

Pay attention to automatic mixed precision: it will speed up the training
process (by itself and because it allows to increase batch size). However,
this is only viable when you are experimenting on hyper-parameters. Proper
selection of best evaluating model seems to vary much more when AMP is enabled
than when it is disabled. So use with caution when tuning parameters and
disable it when making a release.
￼
Default values should provide good experience.

The default batch size has been tested with this mix of dataset:
 - Common Voice French, released on 2019 december 10th
 - FIXME

### Transfer learning from English

To perform transfer learning, please download and make a read-to-use directory
containing the checkpoint to use. Ready-to-use means directly re-usable checkpoints
files, with proper `checkpoint` descriptor as TensorFlow produces.

To use an existing checkpoint, just ensure the `docker run` includes a mount such as:
`type=bind,src=PATH/TO/CHECKPOINTS,dst=/transfer-checkpoint`. Upon running, data
will be copied from that place.

## Hardware

Training successfull on:
 - 64GB RAM
 - 2x RTX 2080 Ti
 - Debian Sid, kernel 5.2, driver 430.50
 - With ~250h of audio, one training epoch takes ~15min, and validation takes ~50s

## Run the image:

The `mount` option is really important: this is where intermediate files, training, checkpoints as
well as final model files will be produced.

```
$ docker run --tty --rm --runtime=nvidia --mount type=bind,src=PATH/TO/HOST/DIRECTORY,dst=/mnt <docker-image-id>
```

Training parameters can be changed at runtime as well using environment variables.
