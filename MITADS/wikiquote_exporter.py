#!/usr/bin/env python3
from xml.dom import minidom

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

result = open( './result.txt', 'w' )

text = ''
for elem in items:
    title = elem.getElementsByTagName("title")[0].firstChild.data
    if 'wiki' not in title:
        textdom = elem.getElementsByTagName("revision")[0].getElementsByTagName("text")[0]
        if textdom.firstChild.data is not None:
            textdom = textdom.firstChild.data
            raw_text = "".join(html_escape_table.get(c,c) for c in str(textdom)).splitlines()
            for line in raw_text:
                if line.startswith('=') or line.startswith('{'):
                    continue

                if line.find("''") >= 0:
                    continue

                text += line

            text = text.replace('. ', "\n")
            result.write(text)

result.close()
