# DeepSpeech Italian Model

*Read this in other languages: [Italian](README.it-IT.md)*

Aggregator of tools for generating a machine learning model for the Italian language of the Common Voice project. You can find us on Telegram with our bot [@mozitabot](https://t.me/mozitabot) in the Developers group where we direct and discuss development or on the [forum](https://discourse.mozilla.org/c/community-portal/mozilla-italia).

---

## Rules

* Ticket and pull requests in English
* Readme in Italian

## Requirements

Python 3.7+

## Quick Start

### Use colab:
</br>

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/MozillaItalia/DeepSpeech-Italian-Model)

### or:
```bash

   # Activate a virtualenv
   virtualenv -p python3 $HOME/tmp/deepspeech-venv/
   source $HOME/tmp/deepspeech-venv/bin/activate

   # Install DeepSpeech
   pip3 install deepspeech==0.9.3

   # Download and unpack the files for the Italian model (check the latest version released!)
   curl -LO https://github.com/MozillaItalia/DeepSpeech-Italian-Model/releases/download/2020.08.07/model_tensorflow_it.tar.xz
   tar xvf model_tensorflow_en.tar.xz

   # Or use the Italian model with transfer learning from the English one (check the latest released version!)
   curl -LO https://github.com/MozillaItalia/DeepSpeech-Italian-Model/releases/download/2020.08.07/transfer_model_tensorflow_it.tar.xz
   tar xvf transfer_model_tensorflow_en.tar.xz

   # extract a random sample from the cv_tiny dataset
   wget -c https://github.com/MozillaItalia/DeepSpeech-Italian-Model/files/4610711/cv-it_tiny.tar.gz -O - | tar -xz common_voice_en_19574474.wav

   # Transcribe (MONO audio, WAV format and sampled at 16000Hz)
   deepspeech --model output_graph.pbmm --scorer scorer --audio common_voice_en_19574474.wav
```

### Differences between pure italian model and with transfer learning

From 08/2020 we release the model in two versions, one "from scratch" that is only Italian language dataset (specified in the release) and another version trained with transfer learning technique.  
The second one is trained from the official model checkpoint released by Mozilla, which includes other datasets in addition to the Common Voice one, exceeding more than 7000 hours of material. This model proved to be much more reliable in recognition given the few hours of Italian language that we have at the moment.

## Development

### Corpora for the language model

In the folder MITADS there are all the scripts that allow the generation of the textual corpus [MITADS](https://github.com/MozillaItalia/DeepSpeech-Italian-Model/releases/tag/Mitads-1.0.0-alpha2). Please refer to the [related README](MITADS/README.md) for more information.

### Model Training

Refer to the [README](DeepSpeech/README.md) in the DeepSpeech folder for the documentation needed to create the Docker image used to train the acoustic and language model.

### Generate the model with COLAB [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/MozillaItalia/DeepSpeech-Italian-Model)

Refer to the [README in notebooks](notebooks/README.md).

### How to program with DeepSpeech

Refer to our [wiki](https://github.com/MozillaItalia/DeepSpeech-Italian-Model/wiki) under construction which contains links and other material.

### Resources

* [Roadmap for Development](https://docs.google.com/document/d/1cep28JAv9f90LkIpVmJjR0lTDqW5Hp_YF7R-nVJ2zkY/edit)
* [Sample package on how the Common Voice dataset is structured](https://github.com/MozillaItalia/DeepSpeech-Italian-Model/files/4610711/cv-it_tiny.tar.gz)
* Examples of minimal dataset importer: ldc93s1 [python for DeepSpeech](https://github.com/mozilla/DeepSpeech/blob/master/bin/import_ldc93s1.py) and [bash launcher](https://github.com/mozilla/DeepSpeech/blob/master/bin/run-ldc93s1.sh)
* https://voice.mozilla.org/it
* https://github.com/mozilla/DeepSpeech
* https://github.com/mozilla/voice-corpus-tool
* https://github.com/Common-Voice/sentence-collector
* https://github.com/Common-Voice/commonvoice-fr - The repository from which this is derived
* https://github.com/MozillaItalia/voice-web - The primary dataset of Italian phrases we maintain here
