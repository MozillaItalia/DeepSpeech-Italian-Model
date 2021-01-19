DeepSpeech ITA
=================
*Read this in other languages: [Italian](README.it-IT.md)*

* [Generate the model](#generate)
  * [CommonVoice Dataset](#cv)
  * [Create Docker Image](#docker)
  * [Start training](#training)
  * [Execute individual steps](#steps)
* [Docker container configuration](#config)
  * [Env files](#env_files)
* [Parameter list](#params)


<a name="generate"></a>
## Generate the model

#### Warning!
Before we start, the new Deepspeech Docker base image needs [nvidia-docker](https://github.com/NVIDIA/nvidia-docker).

In the README of the NVIDIA repository you will find instructions depending on your system.

During the training process the folder ``$HOME/data`` will take up several tens of GB of disk space. If you want to use another folder (e.g. on another partition) replace in _all_ the following commands ``$HOME/data`` with the path to the new folder.

<a name="cv"></a>
### Prepare CommonVoice dataset

* Download the dataset [CommonVoice italian](https://commonvoice.mozilla.org/it/datasets) in ``$HOME/data``


```bash
 cd $HOME
 mkdir -p data/sources
 chmod a+rwx -R data
 mv en.tar.gz data/sources # version 3 of common voice
 chmod a+r data/sources/en.tar.gz
 ```

 <a name="docker"></a>
### Create the Docker image

```bash
cd $HOME
git clone MozillaItalia/DeepSpeech-Italian-Model.git

cd DeepSpeech-Italian-Model/DeepSpeech
chmod +x generate_base_dockerfile.sh
./generate_base_dockerfile.sh

# build base
docker build . -f Dockerfile.train -t deepspeech/base:0.9.3
# Italian build
docker build . -f Dockerfile_it.train -t deepspeech/it
```

 <a name="training"></a>
### Start training

 * Starting the image will run the training routine with the values already preset in the Dockerfile:


 ```bash
 docker run --rm --gpus all --mount type=bind,src=$HOME/data,dst=/mnt -it deepspeech/it
```
* **WARNING** The real training step can be executed only with the user interaction (`Press a button to continue..`) allowing a final check of the parameters that will be passed to DeepSpeech.

* After the execution in the directory `$HOME/data` or in the directory `/mnt` in the Docker container, the files will be created:
    * `it-it.zip` containing the TFlite model.
    * `mode_tensorflow_it.tar.xz` containing the memory mapped model
    * `checkpoint_en.tar.xz` containing the last checkpoint from the validation set

<a name="steps"></a>
### Execute individual steps

You can override Docker's `entrypoint` statement to use the container shell. This way the various scripts can be started individually for experimentation.

For more information on the role of the various scripts see the related [README](en/README.md)

```bash
docker run --rm --gpus all --mount type=bind,src=$HOME/data,dst=/mnt --entrypoint /bin/bash -it deepspeech/it
```

<a name="config"></a>
## Docker container configuration

You can change the parameters set in the ``Dockerfile_en.train`` using the ``-e`` flag followed by the variable name and its new value.

```bash
 docker run -e "TRANSFER_LEARNING=1" -e "DROP_SOURCE_LAYERS=3" --rm --gpus all --mount type=bind,src=$HOME/data,dst=/mnt -it deepspeech/en
```

<a name="env_files"></a>
### .env files

In combination with the ``-e`` flag it is possible to modify the Dockerfile parameters with a ``.env`` file containing the list of parameters to be passed.

Some example ```.env``` files are present in the ``DeepSpeech/env_files`` folder and can be passed via the ``--env-file`` flag to the Docker ``run``.

* ``fast_dev.env``: each step of DeepSpeech training will be run fast to test each step.

```bash
cat fast_dev.env
  BATCH_SIZE=2
  EPOCHS=2
  FAST_TRAIN=1
docker run --env-file env_files/fast_dev.env --rm --gpus all --mount type=bind,src=$HOME/data,dst=/mnt -it deepspeech/en
```

* ```do_transfer_learning.env```: the flag ```DROP_SOURCE_LAYERS=1``` is added and the checkpoint of the DeepSpeech English model will be used.

* ```only_export.env```: if a checkpoint of a previous iteration is present, the training phase is skipped and the various binary files of the model are created

* ``run_lm_optimizer.env``: the flag ```LM_EVALUATE_RANGE=5,5,600``` is updated to run the script ```lm_optimizer.py``` over 600 iterations to find the best values of ``ALPHA`` and ``BETA`` over a range ``[5,5]``

<a name="params"></a>
### Parameters list

More details on the meaning of the following flags and parameters can be found [HERE](http://deepspeech.readthedocs.io/en/v0.8.0/Flags.html)

| PARAMETER | VALUE | notes |
| ------------- | ------------- | ------------- |
| `BATCH_SIZE` | `64` |
| `EPOCHS` | `30` | number of iterations
| `LEARNING_RATE`| `0.0001` |
| `N_HIDDEN`| `2048` |
| `EARLY_STOP`| `1` | if `1`, after `ES_STOP` iterations the loss value of the model does not improve, the training stops
| `ES_STOP` | `10` | Default in English DeepSpeech: `25`
| `MAX_TO_KEEP` | `2` | how many checkpoints to save. Default in DeepSpeech English: `5`
| `DROPOUT` | `0.4` |
| `LM_ALPHA` | `0` |
| `LM_BETA` | `0` |
| `LM_EVALUATE_RANGE`| - | triplet of values `MAX_ALPHA,MAX_BETA,N_TRIALS` to be assigned to the script `lm_optimizer.py` (e.g. `5,5,600`)
| `AMP` | `1` | if `TRANSFER_LEARNING` enabled, this parameter is disabled. More information [HERE](https://deepspeech.readthedocs.io/en/v0.8.0/TRAINING.html?highlight=automatic%20mixed%20precision#training-with-automatic-mixed-precision)
| `TRANSFER_LEARNING` | `0` | if `1`, `DROP_SOURCE_LAYERS` is set to `1` and start learning from the English DeepSpeech checkpoint discarding the last layer of the network (more info [HERE](https://deepspeech.readthedocs.io/en/v0.8.0/TRAINING.html#transfer-learning-new-alphabet))
| `FAST_TRAIN` | 0 | if `1` you start a fast training just to check that all steps are successful
