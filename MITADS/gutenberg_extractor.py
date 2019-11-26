#!/usr/bin/env python3
from gutenberg.acquire import load_etext
from gutenberg.cleanup import strip_headers
from typing.re import Pattern
import roman
import re

ids = open( './books_list.txt', 'r' ).read().splitlines()
text = ''

mapping_normalization = [
  #[ u'\xa0 ', u' ' ],
#  [ u'«\xa0', u'«' ],
#  [ u'\xa0»', u'»' ],
  #[ u'\xa0' , u' ' ],
  [ u'M.\u00a0'   , u'Monsieur ' ],
  [ u'M. '   , u'Monsieur ' ],
  [ u'Mme\u00a0'  , u'Madame ' ],
  [ u'Mme '  , u'Madame ' ],
  [ u'Mlle\u00a0' , u'Mademoiselle ' ],
  [ u'Mlle ' , u'Mademoiselle ' ],
  [ u'Mlles\u00a0', u'Mademoiselles ' ],
  [ u'Mlles ', u'Mademoiselles ' ],
  [ u'%', u'pourcent' ],
  [ u'arr. ', u'arrondissement ' ],
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
    #print('maybe_normalize', 'ro=', ro)
    try:
      value = value.replace(ro_before + ro + ro_after, ro_before + str(roman.fromRoman(ro)) + ro_after)
    except roman.InvalidRomanNumeralError as ex:
      print(ex)
      pass

  return value


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


for book_id in ids:
    print('Downloading Gutenberg book '+ book_id)
    # Based on https://github.com/Common-Voice/commonvoice-fr/blob/master/CommonVoice-Data/project-gutenberg.py
    this_line = 0
    has_title = False
    mainpage_marker    = '    '
    has_mainpage       = False
    has_start_mainpage = False
    has_end_mainpage   = False

    extext = load_etext(int(book_id))
    text += strip_headers(extext).strip()
    search_for_mainpage_marker = len(list(filter(lambda x: x.startswith(mainpage_marker), text))) > 0

    # Cleaning
    for line in text:
        this_line += 1

        if len(line) == 0:
            continue

        if not has_title:
            if (search_for_mainpage_marker and line.startswith(mainpage_marker)) or True:
                if line.isupper():
                    has_title = True
            continue

        if not has_mainpage:
            if not has_start_mainpage:
                if (search_for_mainpage_marker and line.startswith(mainpage_marker)) or True:
                    has_start_mainpage = True
                continue
            else:
                if (search_for_mainpage_marker and line.startswith(mainpage_marker)) or True:
                    has_end_mainpage = True
                else:
                    continue

            has_mainpage = has_start_mainpage and has_end_mainpage

        if line.startswith('  '):
            continue

        if line.isupper():
            continue

        if line.find('[') >= 0 or line.find(']') >= 0:
            continue

        line = maybe_normalize(line)

        text += line
    # TODO: Strip lines like
    # L. CELLI.--_Le ordinanze militari della Repubblica Veneta nel secolo
    # XVI_.--Nuova Antologia--Vol. LIII--Serie III--Fascicoli del 1
    # settembre e 1 ottobre 1894.
    # Strip stuff like [4]
    # Strip stuff like
    #     *
    #    * *

print('Total words: ' + str(len(text.split())))

result = open( './result.txt', 'w' )
result.write( text )
result.close()
