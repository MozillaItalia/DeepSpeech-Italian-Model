#!/usr/bin/env python3
from xml.dom import minidom
from html import unescape
import re
from utils import sanitize, line_rules, download

download_me = download.Download()
validate_line = line_rules.LineRules()
clean_me = sanitize.Sanitization()

xml_path = download_me.if_not_exist('https://dumps.wikimedia.org/itwikiquote/latest/itwikiquote-latest-pages-articles.xml.bz2').bz2_decompress()

print('  Reading XML file')
mydoc = minidom.parse(xml_path)
items = mydoc.getElementsByTagName('page')

result = open( './output/wikiquote.txt', 'w' )

print('  Parsing in progress')
text = ''
# titles_blacklist = [
#         "Modulo:Arguments/man",
#         "Modulo:Arguments",
#         "Modulo:Wikidata/Sandbox/man",
#         "Modulo:Wikidata",
#         "Modulo:Wikidata/man",
#         "Wikiquote:Elenchi generati offline/Immagini in Wikiquote e Wikipedia/Elenco 2",
#         "Wikiquote:Elenchi generati offline/Immagini in Wikiquote e Wikipedia/Elenco 1"
# ]
words_blacklist = ['|', '{{', ':', '[', 'ISBN', '#', 'REDIRECT', 'isbn', 'RINVIA', 'thumb', 'right']
for elem in items:
    title = elem.getElementsByTagName("title")[0].firstChild.data
    if 'wiki' not in title and title != 'Pagina principale' and 'MediaWiki' not in title:
        # if title not in titles_blacklist:
        if ":" not in title:
            format = elem.getElementsByTagName("revision")[0].getElementsByTagName("format")[0]
            if format.firstChild.data == 'text/x-wiki':
                textdom = elem.getElementsByTagName("revision")[0].getElementsByTagName("text")[0]
                if textdom.firstChild is not None:
                    text = ''
                    raw_text = unescape(textdom.firstChild.data)
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
                              [u'*', u"\n"],
                              [u'<br />', u"\n"],
                              [u'<br>', u"\n"],
                              [u"\(\d\d\d\d\)", ""],
                              [u"[\(\[].*?[\)\]]", ""],
                              ['AvvertenzaContattiDonazioni', '']
                            ], roman_normalization=False)
                    raw_text = clean_me.prepare_splitlines(
                        raw_text).splitlines()

                    for line in raw_text:
                        line = clean_me.clean_single_line(line).strip()

                        if len(line) <= 15:
                            continue

                        if validate_line.startswith(line, ['(', 'vivente)']):
                            continue

                        if validate_line.contain(line, words_blacklist):
                            continue

                        if validate_line.isdigit([line, line[1:], line[:1]]):
                            continue

                        if validate_line.isbookref(line):
                            continue

                        if validate_line.isbrokensimplebracket(line):
                            continue
                        # if this is True it means that it contains forbidden chars
                        if not re.search(r"[^aAàÀbBcCdDeEèÈéÉfFgGhHiIìÌjJkKlLmMnNoOòÒpPqQrRsStTuUùÙvVwWxXyYzZ.;,' ]",line):
                            # a gentle filter that just allow the italian alphabet chars and
                            # prevents lines made up by just symbols (eg . . . . . )
                            if re.search(r"[aAàÀbBcCdDeEèÈéÉfFgGhHiIìÌjJkKlLmMnNoOòÒpPqQrRsStTuUùÙvVwWxXyYzZ]+",line):
                                # delete some repeated symbols
                                # line = re.sub(r"[.,:;!?]{2,}", "", line)
                                line = re.sub(r"[.,:;]{2,}", "", line)
                                line = re.sub(r"AA\. |VV |VV\.|AA\.VV", "", line)
                                text += line + "\n"

                    result.write(text)

result.close()

result = open( './output/wikiquote.txt', 'r' )
text = result.read().splitlines()
result.close()

print(' Total lines: ' + str(len(text)))
