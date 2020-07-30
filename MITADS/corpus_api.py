#!/usr/bin/env python3
import re, os
from utils import download, sanitize
from bs4 import BeautifulSoup
import urllib
downloader = download.Download()
downloader.folder = "./parsing/parlareitaliano/"

url = "http://www.parlaritaliano.it/api/index.php?act=search&subdir=API+corpus%2F.&sortby=name&searchpattern=%5C.hsw%24&regexpsearch=true"
soup = downloader.download_for_bp(url)

clean_me = sanitize.Sanitization()
mapping_normalization = [
    [u'/', u''],
    [re.compile(' <inspirazione> <pb> ([A-Z])'), u'.\n\g<1>'],
    [re.compile(' <pb> <inspirazione> ([A-Z])'), u'.\n\g<1>'],
    [re.compile(' <pl> ([A-Z])'), u'.\n\g<1>'],
    [re.compile('<pb>'), u''],
    [re.compile(' {0,1}<.*?>'), u''],
    [re.compile(' {0,1}/[A-Z]?/'), u''],
    [re.compile(' [A-Za-z]*?\+'), u''],
    [re.compile('\*[A-Za-z]*(( |$)|\+)'), u''],
    [re.compile("(^| )[A-Za-z']+\+( |$)"),u''],
    [re.compile(' {0,1}\[.*?\]'), u''],
    [u'a"', u'à'],
    [u'e"', u'è'],
    [u'i"', u'ì'],
    [u'o"', u'ò'],
    [u'u"', u'ù'],
    [re.compile('IDS: {0,}'), u''],
    [u'{', u''],
    [u'}', u''],
    [u'#', u''],
    [re.compile("(^| )[A-Za-z']+\+"),u''],
    [u'\\', u''],
]
out = open("output/parlareitaliano_corpus_api.txt", "w", encoding="UTF-8")
final = ""
links = soup.find_all('a')
print("Parsing", len(links),"links")
cnt = 0
for link in soup.find_all('a'):
    href = link.get('href')
    if href.endswith(".hsw"):
        fileName = href.split()[-1]
        url = "http://www.parlaritaliano.it"+href
        downloader.if_not_exist(url)
        try:
            # p = downloader.download_page(url, decode="cp1252")
            f = open(downloader.file,"r",encoding="cp1252")
            p = f.read()
        except urllib.error.HTTPError as exc:
            print("error downloading", href, "error:", exc)
            p.close()
        else:
            text = clean_me.maybe_normalize(
                p, mapping=mapping_normalization, roman_normalization=False)

            if len(text) > 5:  # TODO: parametrize?

                out.write(text+"\n")
            f.close()
        cnt+=1
        if (cnt % (len(links)//8)) == 0:
            print("Still parsing..")


out.close()
