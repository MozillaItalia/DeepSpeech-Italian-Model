# Colab notebooks per DeepSpeech

Colab notebooks dedicati allo sviluppo del modello DeepSpeech.
* ```deepspeech_lm.ipynb```: notebook per generare il language model (scorer)
* ```deepspeech_training.ipynb```: notebook dedicato al training con possibilità di fine tuning e transfer learning


## Attenzione!
* Dedicare un po' di tempo a leggere ogni cella del notebook :) non caricarle tutte insieme!  

## Quick Start

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/MozillaItalia/DeepSpeech-Italian-Model)

### o manualmente: 

 * Andare su: https://colab.research.google.com/ con il vostro account Google
 * Se non viene visualizzato il popup per l'upload dei notebooks, andare su ```File -> Open notebook```
 * Selezionare la tab ```Github``` e copincollare l'url al notebook di questa repository
 * Generare il modello del linguaggio caricando il notebook ```deepspeech_lm.ipynb```
 * Salvare il modello del linguaggio generato (```scorer```), caricare il notebook ```deepspeech_training.ipynb``` e copiare nel path corretto lo scorer
 * Modificare a piacimento i parametri di training e divertirsi :)

## Requisiti

* (training) spazio di archiviazione aggiuntivo di Google Drive
  * i dataset attuali CV-IT e M-AILABS occupano ~30GB
* (training) Tipo di istanza: GPU
  * a seconda della GPU assegnata, la memoria disponbile potrebbe non essere sufficiente. Nel caso, diminuire il valore di ```BATCH_SIZE``` . Per vedere le caratteristiche della GPU che si sta usando eseguite una cella con il comando ```!nvidia-smi```
