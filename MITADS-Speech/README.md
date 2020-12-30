 # Perché


# Installazione

* Python 3.7+

```
sudo apt install libdb-dev # per Ubuntu/Debian
pip3 install -r requirements.txt
```

## LABLITA extractor
Il [Corpus bilanciato consultabile LABLITA](http://www.parlaritaliano.it/index.php/it/corpora-di-parlato/646-corpus-bilanciato-consultabile-lablita) è un campionamento del _corpus Stammerjohann_, che raccoglie audio di parlato spontaneo registrato a Firenze nel 1965
L'estrattore non ha bisogno di parametri in ingresso, esegue uno scraping delle pagine liberamente consultabili del sistema [DB-IPIC ](http://www.lablita.it/app/dbipic/)

L'Output contiene tutti i clips .mp3 in Italiano e le trascrizioni che sono salvate in un unico file csv
Totale ore estratte: ? 

## EVALITA2009 extractor
[EVALITA 2009](http://www.evalita.it/2009) è il dataset che è stato distribuito per le sfide negli Speech-Task del Workshop periodico EVALITA nel 2009

L'estrattore non ha bisogno di parametri in ingresso ed utilizza l'utility corpora_importer.py
L'Output contiene i file csv train/dev/test con le tracrizioni associate ai file audio. 
I file .wav origilali erano già nel formato adatto per DeepSpeech.
Totale ore estratte: ? 

## MSPKA extractor
[MSPKA Corpus](http://www.mspkacorpus.it/) (Multi-SPeaKing-style Articulatory Corpus) è un dataset di dati acustici e articolatori paralleli in 3 stili di parlato: letto, iperarticolato, ipoarticolato

L'estrattore non ha bisogno di parametri in ingresso ed utilizza l'utility corpora_importer.py

L'Output contiene i file csv train/dev/test con le tracrizioni associate ai file audio
I file .wav originali sono stati rimodulati a 16bit, mono, 16Khz. 
Totale ore estratte: ? 

## SIWIS extractor
[SIWIS Database](https://www.idiap.ch/project/siwis) è uno speech dataset multilingua con enfasi recitata

L'estrattore non ha bisogno di parametri in ingresso ed utilizza l'utility corpora_importer.py

L'Output contiene i file csv train/dev/test con le tracrizioni associate ai file audio
I file .wav originali sono stati rimodulati a 16bit, mono, 16Khz. 
Totale ore estratte: ? 