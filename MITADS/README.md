*Read this in other languages: [Italian](README.it-IT.md)*
# Why

The purpose is to generate a text corpus with free sources, that the text was written after 1920/30 for a more modern Italian and that the text itself is colloquial.

# Installation

* Python 3.7+

```
sudo apt install libdb-dev # for Ubuntu/Debian
pip3 install -r requirements.txt
```

## Gutenberg extractor

To use the extractor you have to insert in a file called "books_list.txt" the addresses to the pages of the books in html format (with or without images) putting one per line.  
This file is already provided with the script.

## OpenSubTitle exporter

It requires as first parameter the folder with the OpenSubTitles dataset.

## Wikiquote exporter

It requires that the wikiquote dump is downloaded and the xml file extracted. It will automatically extract the content generating a new text file.

## Wikisource extractor
The extractor uses a list with the name of the books to download from wikisource and then processes the txt files of the books one by one and cleans and formats them and then everything is put into a single txt output file.
Additional things to do: add proxies to avoid bans, parallelize for speed

## Eulogos Chat extractor
Starting from the home page of the site, the subpages containing the chat datasets are visited and the content is extracted.
