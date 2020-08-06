#!/usr/bin/env bash
i=0
parsing=''

for f in ./wikisource_importer.py ./opensubtitles_exporter.py ./corpus_api.py ./eulogos_chat_importer.py ./ananas_exporter.py ./tg_ita_exporter.py ./ted_importer.py ./gutenberg_exporter.py ./wikiquote_exporter.py
do
  echo "========="
  echo $f
  echo "========="
  python3 $f
done

# remove previous merged texts
rm ./output/mitads*

# nrTxtFiles=$(ls output/*.txt | wc -l)
for f in ./output/*.txt
do
  if [ -f "$f" ]; then
    i=$((i+1))
    parsing="$parsing $f"
  fi
done
if [ "$i" -eq 0 ]; then
  echo "No text files to merge!"
else
  echo "Processing $i files..."
  echo $parsing
  sed -e 's/^[[:space:]]*//' \
  -e '/^$/d' \
  -e '/../!d' \
  -e 's/[.,!?:;]/ /g' \
  -e 's/[[:space:]]*$//' \
  -e 's/[[:space:]]\{2,\}/ /g' \
  -e '/^zz/d' \
  $parsing | \
  grep -E "^[ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzèÈ][ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzàÀèÈéÉìÌòÒùÙ' ]+$" | \
  sort | uniq > ./output/mitads_.txt


  rm $parsing
  cat ./output/mitads_.txt |sort | uniq > ./output/mitads.txt
  rm ./output/mitads_.txt
  echo "Count lines"
  wc -l ./output/mitads.txt
fi
