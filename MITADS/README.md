# Perchè

Lo scopo è quello di generare un corpus testuale con fonti libere, che il testo sia stato scritto dopo il 1920/30 per un Italiano più moderno e che il testo stesso sia colloquiale.

# Installazione

`sudo apt install libdb-dev`
`pip3 install -r requirements.txt`

## Gutenberg extractor

Per utilizzare l'estrattore vanno inseriti in un file chiamato "books_list.txt" gli indirizzi alle pagine dei libri in formato html (con o senza immagini) mettendone uno per riga.  
Questo file è già fornito con lo script.

## OpenSubTitle exporter

Richiede come primo parametro la cartella con il dataset di OpenSubTitles.

## Wikiquote exporter

Richiede che il dump di wikiquote sia scaricato e il file xml estratto. In automatico estrarra il contenuto generando un nuovo file di testo.

## Wikisource extractor
L'estrattore utilizza una lista con il nome dei libri da scaricare da wikisource e poi processa i file txt dei libri uno ad uno e li pulisce e formatta e poi tutto viene tutto inserito in un unico file txt di output
Cose additionali da fare: aggiungere proxies per evitare ban, parallelizzare per velocità

## Eulogos Chat extractor
A partire dalla home del sito vengono visitate le subpages contenenti i datasets delle chat ed estratto il contenuto.
