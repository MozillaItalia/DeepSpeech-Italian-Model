# Common Voice – DeepSpeech

Aggregatore degli strumenti per la generazione di un modello di machine learning per la lingua Italiana del progetto Common Voice.

## Regole

* Ticket e pull requests in inglese
* Readme in Italiano

## Allentamento

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
$ nvidia-docker run --rm --runtime=nvidia --mount type=bind,src=/home/ubuntu/data,dst=/mnt deepspeech
```

Model at $HOME/data/models/it-it.zip

## Risorse

* https://github.com/mozilla/voice-corpus-tool
* https://github.com/Common-Voice/sentence-collector
* https://github.com/MozillaItalia/voice-web - Il dataset primario di frasi italiane lo manteniamo qui
* https://voice.mozilla.org/it
* https://github.com/mozilla/DeepSpeech
* https://github.com/Common-Voice/commonvoice-fr - il repository da cui questo è derivato
