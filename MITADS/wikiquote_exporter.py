#!/usr/bin/env python3
from xml.dom import minidom
import re
from utils import sanitize, line_rules, download

download_me = download.Download()
validate_line = line_rules.LineRules()
clean_me = sanitize.Sanitization()

xml_path = download_me.ifnotexist('https://dumps.wikimedia.org/itwikiquote/latest/itwikiquote-latest-pages-articles.xml.bz2').bz2_decompress()

print('  Reading XML file')
mydoc = minidom.parse(xml_path)
items = mydoc.getElementsByTagName('page')

result = open( './output/wikiquote.txt', 'w' )

print('  Parsing in progress')
text = ''
for elem in items:
    title = elem.getElementsByTagName("title")[0].firstChild.data
    if 'wiki' not in title:
        textdom = elem.getElementsByTagName("revision")[0].getElementsByTagName("text")[0]
        if textdom.firstChild is not None:
            text = ''
            raw_text = clean_me.escapehtml(textdom.firstChild.data)

            for line in raw_text:
                line = clean_me.maybe_normalize(line, [
                      [ u'*' , u"\n" ],
                      [ u'<br />' , u"\n" ],
                      [ u'<br>' , u"\n" ],
                    ], False)
                line = re.compile(r"""\[\[(File|Category):[\s\S]+\]\]|
                        \[\[[^|^\]]+\||
                        \[\[|\]\]|
                        \'{2,5}|
                        (<s>|<!--)[\s\S]+(</s>|-->)|
                        {{[\s\S\n]+?}}|
                        <.*?>|
                        ={1,6}""", re.VERBOSE).sub("",  line)
                line = re.sub("[\(\[].*?[\)\]]", "",  line)

                if len(line) <= 15:
                    continue

                if validate_line.startswith(line, ['(']):
                    continue

                if validate_line.contain(line, ['|', '{{']) or line.find(':') >= 2:
                    continue

                stripped = line.strip()
                if validate_line.isdigit([stripped, stripped[1:], stripped[:1]]):
                    continue

                text += line

            result.write(text)
            
result.close()

result = open( './output/wikiquote.txt', 'r' )
text = clean_me.splitlines(result.read().splitlines())
result.close()

result = open( './output/wikiquote.txt', 'w' )
result.write(text)
result.close()

print(' Total words: ' + str(len(text.split())))
