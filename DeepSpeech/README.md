DeepSpeech ITA
=================

* [Generare il modello](#generate)
  * [CommonVoice Dataset](#cv)
  * [Creare immagine Docker](#docker)
  * [Avviare l'addestramento](#training)
* [Configurazione del container Docker](#config)
  * [Env files](#env_files)
* [Lista dei parametri](#params)


<a name="generate"></a>
## Generare il modello

#### Attenzione!
Prima di iniziare, la nuova immagine base Docker di Deepspeech necessita di [nvidia-docker](https://github.com/NVIDIA/nvidia-docker).

Nel README della repository di NVIDIA trovate le istruzioni a seconda del vostro sistema.

<a name="cv"></a>
### Preparare il dataset di CommonVoice

* Scaricare il dataset [CommonVoice italiano](https://commonvoice.mozilla.org/it/datasets) in ```$HOME/data```

```bash
 cd $HOME
 mkdir -p data/sources
 chmod a+rwx -R data
 mv it.tar.gz data/sources # versione 3 di common voice
 chmod a+r data/sources/it.tar.gz
 ```

 <a name="docker"></a>
### Creare l'immagine Docker

```bash
cd $HOME
git clone MozillaItalia/DeepSpeech-Italian-Model.git

cd DeepSpeech-Italian-Model/DeepSpeech
chmod +x generate_base_dockerfile.sh
./generate_base_dockerfile.sh

# build base
docker build . -f Dockerfile.train -t deepspeech/base:0.8.0
# build italiana
docker build . -f Dockerfile_it.train -t deepspeech/it
```

 <a name="training"></a>
### Avviare l'addestramento

 * Avviando l'immagine verrà eseguita la  routine di addestramento di default:


 ```bash
 docker run --rm --gpus all --mount type=bind,src=$HOME/data,dst=/mnt deepspeech
```

* Terminata l'esecuzione nella directory `$HOME/data` o nella directory `/mnt` nel container Docker, verranno creati i files:
    * `it-it.zip` contenente il modello TFlite
    * `mode_tensorflow_it.tar.xz` contenente il modello memory mapped
    * `checkpoint_it.tar.xz` contenente l'ultimo checkpoint dal validation set

<a name="config"></a>
## Configurazione del container Docker

È possibile modificare i parametri impostati nel ```Dockerfile_it.train``` utilizzando il flag ```-e``` seguito dal nome della variabile e il suo nuovo valore.

```bash
 docker run -e "TRANSFER_LEARNING=1" -e "DROP_SOURCE_LAYERS=3" --rm --gpus all --mount type=bind,src=$HOME/data,dst=/mnt deepspeech
```

<a name="env_files"></a>
### .env files

In combinazione al flag ```-e``` è possibile modificare i parametri del Dockerfile con un file ```.env``` contenente la lista dei parametri da passare.

Alcuni ```.env``` files di esempio sono presenti nella cartella ```DeepSpeech/env_files``` e possono essere passati tramite il flag ```--env-file``` al ```run``` di Docker.

* ```fast_dev.env```: ogni passaggio dell'addestramento di DeepSpeech verrà eseguito velocemente per testare ogni step.

```bash
 cat fast_dev.env
BATCH_SIZE=2
EPOCHS=2
FAST_TRAIN=1
 docker run --env-file env_files/fast_dev.env --rm --gpus all --mount type=bind,src=$HOME/data,dst=/mnt deepspeech
```

* ```do_transfer_learning.env```: viene aggiunto il flag ```DROP_SOURCE_LAYERS=1``` e verrà utilizzato il checkpoint del modello inglese di DeepSpeech.

* ```only_export.env```: se presente un checkpoint di una precedente iterazione, viene saltata la fase di addestramento e si procede alla creazione dei vari files binari del modello

* ```run_lm_optimizer.env```: viene aggiornato il flag ```LM_EVALUATE_RANGE=5,5,600``` per avviare lo script ```lm_optimizer.py``` su 600 iterazioni per cercare i migliori valori di ```ALPHA``` e ```BETA``` su un range ```[5,5]```

<a name="params"></a>
### Lista dei parametri

Per approfondire il significato dei flag e parametri seguenti, sono presenti maggiori dettagli [QUI](http://deepspeech.readthedocs.io/en/v0.8.0/Flags.html)

| PARAMETRO   | VALORE | note |
| -------------  | ------------- | ------------- |
| `BATCH_SIZE`   | `64`  |
| `EPOCHS`       | `30`  |numero di iterazioni
| `LEARNING_RATE`| `0.0001`  |
| `N_HIDDEN`| `2048`  |
| `EARLY_STOP`| `1`  | se dopo `ES_STOP` iterazioni il valore loss del modello non migliora, l'addestramento si ferma
| `ES_STOP`      | `10`  | Default in DeepSpeech inglese: `25`
| `MAX_TO_KEEP`      | `2`  | quanti checkpoints salvare. Default in DeepSpeech inglese: `5`
| `DROPOUT`      | `0.4`  |
| `LM_ALPHA`     | `0`  |
| `LM_BETA`      | `0`  |
| `LM_EVALUATE_RANGE`| -  | tripletta di valori `MAX_ALPHA,MAX_BETA,N_TRIALS` da assegnare allo script `lm_optimizer.py` (es `5,5,600`)
| `AMP`      | `1`  | se `TRANSFER_LEARNING` abilitato, questo parametro viene disabilitato. Maggiori informazioni [QUI](https://deepspeech.readthedocs.io/en/v0.8.0/TRAINING.html?highlight=automatic%20mixed%20precision#training-with-automatic-mixed-precision)
| `TRANSFER_LEARNING`      | `0`  | se `1` `DROP_SOURCE_LAYERS` viene impostato a `1` e si avvia l'apprendimento dal checkpoint di DeepSpeech inglese scartando l'ultimo layer della rete (maggiori info [QUI](https://deepspeech.readthedocs.io/en/v0.8.0/TRAINING.html#transfer-learning-new-alphabet))
| `FAST_TRAIN`      | 0  | se `1` si avvia un addestramento rapido solamente per controllare che tutti gli step vadano a buon fine
