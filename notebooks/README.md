# Colab notebooks per DeepSpeech 0.7

Colab notebooks dedicati allo sviluppo del modello DeepSpeech.
* notebook per generare il language model (scorer)
* notebook dedicato al training con possibilità di fine tuning e transfer learning


## Attenzione!
* Una volta collegato un archivio Google Drive, ogni file che viene cancellato da python/script, viene <b>spostato nel cestino</b> del vostro account Drive.  
Ciò comporta che, durante la fase di training, i checkpoints non definitivamente eliminati andranno a <b>saturare tutto lo spazio disponibile!</b>
* Dedicare un po' di tempo a leggere ogni cella del notebook :) non caricarle tutte insieme!  

## Quick Start

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
