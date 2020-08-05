#!/usr/bin/env bash
i=0
parsing=''
loop=0
for f in ./wikisource_importer.py ./opensubtitles_exporter.py ./corpus_api.py ./eulogos_chat_importer.py ./ananas_exporter.py ./tg_ita_exporter.py ./ted_importer.py ./gutenberg_exporter.py ./wikiquote_exporter.py
do
  echo "========="
  echo $f
  echo "========="
  python3 $f
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
        -e '/^$/d' \
        -e '/../!d' \
        -e 's/[.,!?:;]/ /g' \
        -e 's/[[:space:]]*$//' \
        -e 's/[[:space:]]\{2,\}/ /g' \
        -e '/^zz/d' \
        $parsing | \
        grep -E "^[ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzèÈ][ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzàÀèÈéÉìÌòÒùÙ' ]+$" | \
        sort | uniq > ./output/mitads_$loop.txt
        i=0
        parsing=''
    fi
  fi
done

cat ./output/mitads_*.txt |sort | uniq > ./output/mitads.txt
echo "Count lines"
wc -l ./output/mitads.txt
