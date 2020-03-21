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
    if 'wiki' not in title and title != 'Pagina principale':
        textdom = elem.getElementsByTagName("revision")[0].getElementsByTagName("text")[0]
        if textdom.firstChild is not None:
            text = ''
            raw_text = clean_me.escapehtml(textdom.firstChild.data)
            raw_text = re.compile(r"""\[\[(File|Category):[\s\S]+\]\]|
                        \[\[[^|^\]]+\||
                        \[\[|\]\]|
                        \'{2,5}|
                        (<s>|<!--)[\s\S]+(</s>|-->)|
                        (<s>|<!)[\s\S]+(</s>|>)|
                        {{[\s\S\n]+?}}|
                        <.*?>|
                        ={1,6}""", re.VERBOSE).sub("", raw_text)
            raw_text = clean_me.maybe_normalize(raw_text, [
                      [ u'*' , u"\n" ],
                      [ u'<br />' , u"\n" ],
                      [ u'<br>' , u"\n" ],
                      [ u"\(\d\d\d\d\)", ""],
                      [ u"[\(\[].*?[\)\]]", ""],
                      [ 'AvvertenzaContattiDonazioni', '']
                    ], False)
            raw_text = clean_me.splitlines(raw_text).splitlines()

            for line in raw_text:
                line = clean_me.cleansingleline(line).strip()

                if len(line) <= 15:
                    continue

                if validate_line.startswith(line, ['(']):
                    continue

                if validate_line.contain(line, ['|', '{{', ':', '[', 'ISBN', '#']):
                    continue

                if validate_line.isdigit([line, line[1:], line[:1]]):
                    continue
                
                if validate_line.isbookref(line):
                    continue
                
                if validate_line.isbrokensimplebracket(line):
                    continue
                
                text += line + "\n"

            result.write(text)
            
result.close()

result = open( './output/wikiquote.txt', 'r' )
text = result.read().splitlines()
result.close()

print(' Total lines: ' + str(len(text)))
