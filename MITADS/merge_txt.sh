#!/usr/bin/env bash
# https://github.com/lostutils/uq for uniq lines in rust more fast
i=0
parsing=''
loop=0

for f in ./output/ost/*.txt
do
  if [ -f "$f" ]; then
    i=$((i+1))
    parsing="$parsing $f"
    if [ $i -eq 10000 ]; then
        loop=$((loop+1))
        echo "Processing $loop batch of $i files..."
        sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' -e '/^$/d' -e '/../!d' $parsing | uq > ./output/ost_$loop.txt
        i=0
        parsing=''
    fi
  fi
done

cat ./output/ost_*.txt |uq > ./output/ost.txt
