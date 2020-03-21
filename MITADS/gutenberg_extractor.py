#!/usr/bin/env python3
from gutenberg.acquire import load_etext
from gutenberg.cleanup import strip_headers
from utils import sanitize, line_rules

clean_me = sanitize.Sanitization()
validate_line = line_rules.LineRules()

ids = open( './assets/gutenberg_books.txt', 'r' ).read().splitlines()
text = ''

result = open( './output/gutenberg.txt', 'w' )

for book_id in ids:
    print('  Downloading/Reading Gutenberg book '+ book_id)
    # Based on https://github.com/Common-Voice/commonvoice-fr/blob/master/CommonVoice-Data/project-gutenberg.py
    raw_text = strip_headers(load_etext(int(book_id))).splitlines()
    text = ''

    # Cleaning
    for line in raw_text:
        line = clean_me.maybe_normalize(line)
        if len(line) <= 15:
            continue

        if line.isupper():
            continue

        if validate_line.startswith(line, ['(', '...']):
            continue

        if validate_line.contain(line, ['§', '=', '--', '~']):
            continue
        
        stripped = line.strip()
        if validate_line.isdigit([stripped, stripped[1:], stripped[:1]]):
            continue

        text += line

    text = clean_me.splitlines(text)
    result.write(text)

result.close()

result = open( './output/gutenberg.txt', 'r' )
print(' Total words: ' + str(len(result.read().split())))
result.close()
