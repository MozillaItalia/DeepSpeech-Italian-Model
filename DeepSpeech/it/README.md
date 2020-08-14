Step per l'addestramento del modello
=================
</br>

Una volta avviato il container Docker gli script che vengono eseguiti sono, in ordine:

| SCRIPT   |  |
| -------------  | ------------- |
| `../check.sh`   | Esegue un semplice check controllando che tutte le directories necessarie siano state create e avvia due iterazioni su un mini dataset  |
| `../generate_alphabet.sh`  | se non è presente il file `/mnt/models/alphabet.txt`, viene preso e copiato da `~/data` |
| `import_cvit_tiny.sh`  | importa il dataset di prova `cv_tiny` se il flag `FAST_TRAIN` è impostato pari a `1` sennò viene saltato  |
| `import_cvit.sh`  | importa il dataset italiano di CommonVoice scompattandolo da `/mnt/sources/it.tar.gz`  |
| `import_m-ailabs.sh`  | scarica e importa il dataset italiano di M-AILABS  |
| `build_lm.sh`  | scarica il corpora `mitads.txt` se non presente e avvia la creazione del package scorer `scorer` dopo aver creato il file `lm.binary` e `vocab-500000.txt` |
| `train.sh`  | avvia l'addestramento vero e proprio solo dopo conferma dell'utente. Se presente il flag `TRANSFER_LEARNING=1` viene scaricato il checkpoint della release inglese, viene aggiunto il flag `DROP_SOURCE_LAYERS=1` e si utilizzano i pesi di tutti i layers ma non dell'ultimo (il layer di output della rete).
| `export.sh`  | Controlla la directory `/mnt/models` e, se non presenti, genera i files binari dei modelli per: Tensorflow, TFLite, zip contenente il modello TFLite e scorer, il modello Tensorflow memory mapped|
| `../package.sh` | Controlla la directory `/mnt` e, se non presenti, genera gli archivi: `model_tensorflow_it.tar.xz` con il file memory mapped, `scorer` e `alphabet.txt`, `model_tflite_it.tar.xz` con il modello TFLite, `scorer` e `alphabet.txt`, `checkpoint_it.tar.xz` con gli ultimi `best_dev_checkpoint_xxx`. Infine copia i files `.zip` in `/mnt/models/` in `/mnt/`
