# Common Voice – DeepSpeech

Aggregatore degli strumenti per la generazione di un modello di machine learning per la lingua Italiana del progetto Common Voice. Ci trovi su Telegram con il nostro bot @mozitabot nel gruppo Developers dove dirigiamo e discutiamo lo sviluppo oppure sul [forum](https://discourse.mozilla.org/c/community-portal/mozilla-italia).

* [Roadmap per lo sviluppo](https://docs.google.com/document/d/1cep28JAv9f90LkIpVmJjR0lTDqW5Hp_YF7R-nVJ2zkY/edit)
* [Script (bash/python) per la generazione usando Docker, DeepSpeech, Tensorflow e Nvidia del modello](https://github.com/MozillaItalia/DeepSpeech-Italian-Model/tree/master/DeepSpeech)
* Il modello generato 
* [Script per generare il corpus testuale per la parte predittiva del modello](https://github.com/MozillaItalia/DeepSpeech-Italian-Model/tree/master/MITADS)
* [Pacchetto di esempio su come è strutturato il dataset di Common Voice](https://github.com/MozillaItalia/DeepSpeech-Italian-Model/files/4610711/cv-it_tiny.tar.gz)

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

```
$ cd $HOME
$ git clone MozillaItalia/DeepSpeech-Italian-Model.git
$ cd DeepSpeech-Italian-Model/DeepSpeech
$ docker build -f Dockerfile.train -t deepspeech .
$ cd $HOME
$ mkdir -p data/sources
$ chmod a+rwx -R data
$ mv it.tar.gz data/sources # versione 3 di common voice
$ chmod a+r data/sources/it.tar.gz
$ docker run --rm --gpus all --mount type=bind,src=/home/ubuntu/data,dst=/mnt deepspeech
```
Model at $HOME/data/models/it-it.zip

To configure docker parameters:
```
$ cat deepspeech.env
EARLY_STOP=0
EPOCHS=20
DROPOUT=0.5
$ docker run --env-file deepspeech.env --rm --gpus all --mount type=bind,src=/home/ubuntu/data,dst=/mnt deepspeech
```

## Risorse

* https://voice.mozilla.org/it
* https://github.com/mozilla/DeepSpeech
* https://github.com/mozilla/voice-corpus-tool
* https://github.com/Common-Voice/sentence-collector
* https://github.com/Common-Voice/commonvoice-fr - Il repository da cui questo è derivato
* https://github.com/MozillaItalia/voice-web - Il dataset primario di frasi italiane lo manteniamo qui
