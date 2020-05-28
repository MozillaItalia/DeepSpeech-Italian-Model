# Colab notebooks per DeepSpeech

Colab notebooks dedicati allo sviluppo del modello DeepSpeech.
* notebook per generare il language model (scorer)
* notebook dedicato al training con possibilità di fine tuning e transfer learning

## Requisiti

* (training) spazio di archiviazione aggiuntivo di Google Drive
  * i dataset attuali CV-IT e M-AILABS occupano ~30GB
* (training) Tipo di istanza: GPU
  * a seconda della GPU assegnata, la memoria disponbile potrebbe non essere sufficiente. Nel caso, diminuire il valore di ```BATCH_SIZE```

## Note

* Una volta collegato un archivio Google Drive, ogni file che viene cancellato da python o script, viene spostato nel cestino del vostro account Drive.  
Ciò comporta che, durante la fase di training, i checkpoints non definitivamente eliminati vanno a saturare tutto lo spazio disponibile!  
