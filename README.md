# DeepSpeech Italian Model

Aggregatore degli strumenti per la generazione di un modello di machine learning per la lingua Italiana del progetto Common Voice. Ci trovi su Telegram con il nostro bot [@mozitabot](https://t.me/mozitabot) nel gruppo Developers dove dirigiamo e discutiamo lo sviluppo oppure sul [forum](https://discourse.mozilla.org/c/community-portal/mozilla-italia).

---

## Regole

* Ticket e pull requests in inglese
* Readme in Italiano

## Requisiti

Python 3.7+

## Quick Start
</br>
</br>

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/MozillaItalia/DeepSpeech-Italian-Model/notebooks)

### oppure
```bash

   # Attiva un virtualenv
   virtualenv -p python3 $HOME/tmp/deepspeech-venv/
   source $HOME/tmp/deepspeech-venv/bin/activate

   # Installa DeepSpeech
   pip3 install deepspeech==0.9.3

   # Scarica e scompatta i file per il modello italiano (verifica l'ultima versione rilasciata!)
   curl -LO https://github.com/MozillaItalia/DeepSpeech-Italian-Model/releases/download/2020.08.07/model_tensorflow_it.tar.xz
   tar xvf model_tensorflow_it.tar.xz

   # Oppure utilizza il modello italiano con transfer learning da quello inglese (verifica l'ultima versione rilasciata!)
   curl -LO https://github.com/MozillaItalia/DeepSpeech-Italian-Model/releases/download/2020.08.07/transfer_model_tensorflow_it.tar.xz
   tar xvf transfer_model_tensorflow_it.tar.xz

   # Trascrivi un file audio MONO, formato WAV e campionato a 16000Hz
   deepspeech --model output_graph.pbmm --scorer scorer --audio your/path/to/audio/sampled_at_16Khz.wav
```

### Differenze del modello italiano puro e con transfer learning

Da 08/2020 rilasciamo il modello in due versioni, puro ovvero solo dataset di lingua italiana (specificato nel release) e la versione con transfer learning.  
La seconda versione include il transfer learning dal modello di lingua ufficiale rilasciato da Mozilla, che include altri dataset oltre a quello di Common Voice superando le oltre 7000 ore di materiale. Questo modello si è dimostrato molto piú affidabile nel riconoscimento viste le poche ore di lingua italiana che disponiamo al momento.

## Sviluppo

### Corpora per il modello del linguaggio

Nella cartella MITADS sono presenti tutti gli script che permettono la generazione del corpus testuale [MITADS](https://github.com/MozillaItalia/DeepSpeech-Italian-Model/releases/tag/Mitads-1.0.0-alpha2). Per maggiori informazioni fare riferimento al [README relativo](MITADS/README.md).

### Addestramento del modello

Fare riferimento al [README](DeepSpeech/README.md) nella cartella DeepSpeech per la documentazione necessaria per creare l'immagine Docker utilizzata per addestrare il modello acustico e del linguaggio.

### Generare il modello con COLAB

Fare riferimento al [README in notebooks](notebooks/README.md).

### Come programmare con DeepSpeech

Fare riferimento al nostro [wiki](https://github.com/MozillaItalia/DeepSpeech-Italian-Model/wiki) in costruzione che contiene link e altro materiale.

### Risorse

* [Roadmap per lo sviluppo](https://docs.google.com/document/d/1cep28JAv9f90LkIpVmJjR0lTDqW5Hp_YF7R-nVJ2zkY/edit)
* [Pacchetto di esempio su come è strutturato il dataset di Common Voice](https://github.com/MozillaItalia/DeepSpeech-Italian-Model/files/4610711/cv-it_tiny.tar.gz)
* Esempi di importatore di dataset minimali: ldc93s1 [python per DeepSpeech](https://github.com/mozilla/DeepSpeech/blob/master/bin/import_ldc93s1.py) e [lanciatore bash](https://github.com/mozilla/DeepSpeech/blob/master/bin/run-ldc93s1.sh)
* https://voice.mozilla.org/it
* https://github.com/mozilla/DeepSpeech
* https://github.com/mozilla/voice-corpus-tool
* https://github.com/Common-Voice/sentence-collector
* https://github.com/Common-Voice/commonvoice-fr - Il repository da cui questo è derivato
* https://github.com/MozillaItalia/voice-web - Il dataset primario di frasi italiane lo manteniamo qui
