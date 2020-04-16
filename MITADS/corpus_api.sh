#!/usr/bin/env bash
python corpus_api.py && sort parlareitaliano_corpus_api.txt | uniq -u - > ./output/corpus_api.txt
