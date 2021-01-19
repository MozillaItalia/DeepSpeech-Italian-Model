# Colab notebooks per DeepSpeech
*Read this in other languages: [Italian](README.it-IT.md)*

Colab notebooks dedicated to the development of the DeepSpeech model.
* ``deepspeech_lm.ipynb``: notebook to generate the language model (scorer)
* ``deepspeech_training.ipynb``: notebook dedicated to the training with possibility of fine tuning and transfer learning


## Attention!
* Take some time to read each cell of the notebook :) don't load them all at once!  

## Quick Start

### Just click here:
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/MozillaItalia/DeepSpeech-Italian-Model)

### or manually:

 * go to: https://colab.research.google.com/ with your Google account
 * If you don't see the popup for uploading notebooks, go to ``File -> Open notebook``
 * Select the tab ``Github`` and copy-paste the url to the notebook of this repository
 * Generate the language model by loading the notebook ``deepspeech_lm.ipynb``.
 * Save the generated language model (``scorer``), load the notebook ``deepspeech_training.ipynb`` and copy the scorer to the correct path.
 * Modify the training parameters at will and have fun :)

## Requirements

* (training) additional Google Drive storage space
  * current CV-IT and M-AILABS datasets occupy ~30GB
* (training) Instance type: GPU
  * depending on the assigned GPU, the available memory may not be enough. In case, decrease the value of ``BATCH_SIZE`` . To see the characteristics of the GPU you are using run a cell with the command ``!nvidia-smi``
