#!/usr/bin/env python3
import re
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
    raw_text = strip_headers(load_etext(int(book_id)))
    # removes multiple marks
    mapping_normalization = [
            [re.compile("[.,:;]{2,}"), u' ']
    ]
    raw_text = clean_me.maybe_normalize(
        raw_text, mapping=mapping_normalization, mapping_prepend=False)

    raw_text = clean_me.prepare_splitlines(raw_text).splitlines()

    text = ''

    # Cleaning
    for line in raw_text:
        line = clean_me.clean_single_line(line).strip()
        if len(line) <= 15:
            continue

        if line.isupper():
            continue

        if validate_line.startswith(line, ['(', '...']):
            continue

        if validate_line.contain(line, ['§', '=', '--', '~', '   ', '[']):
            continue

        if validate_line.isdigit([line, line[1:], line[:1]]):
            continue

        text += line + "\n"

    result.write(text)

result.close()

result = open( './output/gutenberg.txt', 'r' )
print(' Total lines: ' + str(len(result.read().splitlines())))
result.close()
