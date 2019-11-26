#!/usr/bin/env python3
from gutenberg.acquire import load_etext
from gutenberg.cleanup import strip_headers
from typing.re import Pattern
import roman
import re

ids = open( './gutenberg_books.txt', 'r' ).read().splitlines()
text = ''

mapping_normalization = [
  #[ u'\xa0 ', u' ' ],
  [ u'«', u'' ],
  [ u'»', u'' ],
  [ u'×' , u'' ],
  [ u'_' , u'' ],
  [ u'-' , u'' ],
  [ u'—' , u'' ],
  [ u'* * * ' , u'' ],
  [ u'( ' , u'' ],
  [ u' , ' , u', ' ],
  [ u' )' , u'' ],
  [ u'Sig. '   , u'Signor ' ],
  [ re.compile('\[\d+\]'), u'' ],
]

def maybe_normalize(value, mapping=mapping_normalization):
  for norm in mapping:
    if type(norm[0]) == str:
      value = value.replace(norm[0], norm[1])
    elif isinstance(norm[0], Pattern):
      value = norm[0].sub(norm[1], value)
    else:
      print('UNEXPECTED', type(norm[0]), norm[0])

  for ro_before, ro_after, ro in getRomanNumbers(value):
    try:
      value = value.replace(ro_before + ro + ro_after, ro_before + str(roman.fromRoman(ro)) + ro_after)
    except roman.InvalidRomanNumeralError as ex:
      print(ex)
      pass

  if value.startswith(';'):
      value = value[1:]

  return value.replace('  ', " ")


def getRomanNumbers(ch):
  ROMAN_CHARS = "XVI"
  ro  = ''
  ros = 0
  for i in range(len(ch)):
    c = ch[i]
    if c in ROMAN_CHARS:
      if len(ro) == 0 and not ch[i-1].isalpha():
        ro  = c
        ros = i
      else:
        if len(ro) > 0 and ch[i-1] in ROMAN_CHARS:
          ro += c
    else:
      if len(ro) > 0:
        if not c.isalpha():
          yield ch[ros-1], ch[i], ro
        ro  = ''
        ros = i

  if len(ro) > 0:
    yield ch[ros-1], '', ro


result = open( './result.txt', 'w' )

for book_id in ids:
    print('Downloading Gutenberg book '+ book_id)
    # Based on https://github.com/Common-Voice/commonvoice-fr/blob/master/CommonVoice-Data/project-gutenberg.py
    raw_text = strip_headers(load_etext(int(book_id))).splitlines()
    text = ''

    # Cleaning
    for line in raw_text:
        line = maybe_normalize(line)
        if len(line) <= 15:
            continue

        if line.isupper():
            continue

        if line.startswith('(') or line.startswith('...'):
            continue

        if line.find('§') >= 0 or line.find('=') >= 0 or line.find('--') >= 0 or line.find('~') >= 0:
            continue

        if  line.strip().isdigit() or line.strip()[1:].isdigit() or line.strip()[:1].isdigit():
            continue

        text += line

    text = text.replace('. ', "\n")
    result.write(text)

result.close()

result = open( './result.txt', 'r' )
print('Total words: ' + str(len(result.read().split())))
result.close()
