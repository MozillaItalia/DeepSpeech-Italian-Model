#!/usr/bin/env bash
i=0
parsing=''
loop=0
for f in ./corpus_api.py ./eulogos_chat_importer.py ./ananas_exporter.py
do
  python $f
done
nrTxtFiles=$(ls output/*.txt | wc -l)
for f in ./output/*.txt
do
  if [ -f "$f" ]; then
    i=$((i+1))
    parsing="$parsing $f"
    #grep A-Za-z includes annoying chars like °
    if [ $i -eq $nrTxtFiles ]; then
        loop=$((loop+1))
        echo "Processing $loop batch of $i files..."
        sed -e 's/^[[:space:]]*//' \
        -e 's/[[:space:]]*$//' \
        -e '/^$/d' \
        -e '/../!d' \
        -e 's/[[:space:]]\{2,\}/ /g' \
        $parsing | \
        grep -E "^[ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0-9àÈÉèìéòù,;:'. ]+$" | \
        sort | uniq > ./output/ost_$loop.txt
        i=0
        parsing=''
    fi
  fi
done

cat ./output/ost_*.txt |sort | uniq > ./output/ost.txt
