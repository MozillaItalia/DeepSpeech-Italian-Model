# Common Voice – DeepSpeech

Aggregatore degli strumenti per la generazione di un modello di machine learning per la lingua Italiana del progetto Common Voice. Ci trovi su Telegram con il nostro bot @mozitabot nel gruppo Developers dove dirigiamo e discutiamo lo sviluppo oppure sul [forum](https://discourse.mozilla.org/c/community-portal/mozilla-italia).

* [Roadmap per lo sviluppo](https://docs.google.com/document/d/1cep28JAv9f90LkIpVmJjR0lTDqW5Hp_YF7R-nVJ2zkY/edit)
* [Script (bash/python) per la generazione usando Docker, DeepSpeech, Tensorflow e Nvidia del modello](https://github.com/MozillaItalia/DeepSpeech-Italian-Model/tree/master/DeepSpeech)
* Il modello generato
* [Script per generare il corpus testuale per la parte predittiva del modello](https://github.com/MozillaItalia/DeepSpeech-Italian-Model/tree/master/MITADS)
* [Pacchetto di esempio su come è strutturato il dataset di Common Voice](https://github.com/MozillaItalia/DeepSpeech-Italian-Model/files/4610711/cv-it_tiny.tar.gz)
* Esempi di importatore di dataset minimali: ldc93s1 [python per DeepSpeech](https://github.com/mozilla/DeepSpeech/blob/master/bin/import_ldc93s1.py) e [lanciatore bash](https://github.com/mozilla/DeepSpeech/blob/master/bin/run-ldc93s1.sh)

## Regole

* Ticket e pull requests in inglese
* Readme in Italiano

## Utilizzare il modello

Scarica [l'ultima versione](https://github.com/MozillaItalia/DeepSpeech-Italian-Model/releases) da questa pagina.  
Puoi provare il modello con un [bot Telegram](https://t.me/DeepSpeechItalianBot) che compara il vocale con Google Speech.  

```
$ virtualenv test --python=python3
$ source test/bin/activate
$ pip install deepspeech==0.7.0a1
$ deepspeech --model output_graph.pbmm --audio test.wav --trie trie --lm lm.binary
```

## Generare il modello

#### Attenzione!
Prima di iniziare, la nuova immagine base Docker di Deepspeech necessita di [nvidia-docker](https://github.com/NVIDIA/nvidia-docker).

Nel README della repository di NVIDIA trovate le istruzioni a seconda del vostro sistema.


Create inizialmente l'immagine base di Deepspeech, attualmente alla versione 0.8.0:
```
$ cd $HOME
$ git clone MozillaItalia/DeepSpeech-Italian-Model.git
$ cd DeepSpeech-Italian-Model/DeepSpeech
$ chmod +x generate_base_dockerfile.sh
$ ./generate_base_dockerfile.sh
$ docker build . -f Dockerfile.train -t deepspeech/base:0.8.0
```

Successivamente eseguire:
```
$ docker build . -f Dockerfile_it.train -t deepspeech/it
```
Scaricare il dataset CommonVoice italiano in ```$HOME/data```
```
$ cd $HOME
$ mkdir -p data/sources
$ chmod a+rwx -R data
$ mv it.tar.gz data/sources # versione 3 di common voice
$ chmod a+r data/sources/it.tar.gz
$ docker run --rm --gpus all --mount type=bind,src=$HOME/data,dst=/mnt deepspeech
```

Per configurare i parametri del Dockerfile, creare un file con la lista dei parametri e passarlo al run di Docker.

Ad esempio caricando il file ```fast_dev.env``` ogni passaggio dell'addestramento di DeepSpeech verrà eseguito velocemente per testare ogni step.

```
$ cat fast_dev.env
BATCH_SIZE=2
EPOCHS=2
FAST_TRAIN=1
$ docker run --env-file env_files/fast_dev.env --rm --gpus all --mount type=bind,src=$HOME/data,dst=/mnt deepspeech
```

## Generare il modello con notebook COLAB

Fare riferimento al [README in notebooks](https://github.com/MozillaItalia/DeepSpeech-Italian-Model/blob/master/notebooks/README.md)

## Risorse

* https://voice.mozilla.org/it
* https://github.com/mozilla/DeepSpeech
* https://github.com/mozilla/voice-corpus-tool
* https://github.com/Common-Voice/sentence-collector
* https://github.com/Common-Voice/commonvoice-fr - Il repository da cui questo è derivato
* https://github.com/MozillaItalia/voice-web - Il dataset primario di frasi italiane lo manteniamo qui
