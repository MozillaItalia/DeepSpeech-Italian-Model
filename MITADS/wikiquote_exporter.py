#!/usr/bin/env python3
from xml.dom import minidom
from typing.re import Pattern
import re

# Download and extract from https://dumps.wikimedia.org/itwikiquote/latest/itwikiquote-latest-pages-articles.xml.bz2
mydoc = minidom.parse('itwikiquote-latest-pages-articles.xml')
items = mydoc.getElementsByTagName('page')

html_escape_table = {
     "&amp;": "&",
     '&quot;': '"',
     "&apos;": "'",
     "&gt;": ">",
     "&lt;": "<",
     }

mapping_normalization = [
  [ u'«', u'' ],
  [ u'»', u'' ],
  [ u'×' , u'' ],
  [ u'_' , u'' ],
  [ u'-' , u'' ],
  [ u'—' , u'' ],
  [ u'* * * ' , u'' ],
  [ u'*' , u"\n" ],
  [ u'( ' , u'' ],
  [ u' , ' , u', ' ],
  [ u' )' , u'' ],
  [ u'<br />' , u"\n" ],
  [ u'<br>' , u"\n" ],
  [ u'Sig. '   , u'Signor ' ],
  [ re.compile('\[\d+\]'), u'' ],
]

result = open( './result.txt', 'w' )

RE = re.compile(r"""\[\[(File|Category):[\s\S]+\]\]|
        \[\[[^|^\]]+\||
        \[\[|
        \]\]|
        \'{2,5}|
        (<s>|<!--)[\s\S]+(</s>|-->)|
        {{[\s\S\n]+?}}|
        <.*?>|
        ={1,6}""", re.VERBOSE)


def loads(wiki, compress_spaces=None):
    '''
    Parse a string to remove and replace all wiki markup tags
    '''
    result = RE.sub('', wiki)
    if compress_spaces:
        result = re.sub(r' +', ' ', result)

    return result


def load(stream, compress_spaces=None):
    '''
    Parse the content of a file to un-wikified text
    '''
    return loads(stream.read(), compress_spaces=compress_spaces)

def maybe_normalize(value, mapping=mapping_normalization):
  for norm in mapping:
    if type(norm[0]) == str:
      value = value.replace(norm[0], norm[1])
    elif isinstance(norm[0], Pattern):
      value = norm[0].sub(norm[1], value)
    else:
      print('UNEXPECTED', type(norm[0]), norm[0])

  return loads(value)


text = ''
for elem in items:
    title = elem.getElementsByTagName("title")[0].firstChild.data
    if 'wiki' not in title:
        textdom = elem.getElementsByTagName("revision")[0].getElementsByTagName("text")[0]
        if textdom.firstChild is not None:
            text = ''
            textdom = textdom.firstChild.data
            raw_text = "".join(html_escape_table.get(c,c) for c in str(textdom)).splitlines()

            for line in raw_text:
                line = maybe_normalize(line)
                if len(line) <= 15:
                    continue

                if line.startswith('('):
                    continue

                if line.find('|') >= 0 or line.find('{{') >= 0 or line.find(':') >= 2:
                    continue

                if  line.strip().isdigit() or line.strip()[1:].isdigit() or line.strip()[:1].isdigit():
                    continue

                text += line

            result.write(text)

result.close()
