import re, os
from utils import download, sanitize
from bs4 import BeautifulSoup
import urllib
downloader = download.Download()
url = "http://www.parlaritaliano.it/api/index.php?act=search&subdir=API+corpus%2F.&sortby=name&searchpattern=%5C.hsw%24&regexpsearch=true"
soup = downloader.download_for_bp(url)

clean_me = sanitize.Sanitization()
mapping_normalization = [
    [re.compile(' <inspirazione> <pb> ([A-Z])'), u'.\n\g<1>'],
    [re.compile(' <pb> <inspirazione> ([A-Z])'), u'.\n\g<1>'],
    [re.compile(' <pl> ([A-Z])'), u'.\n\g<1>'],
    [re.compile('<pb>'), u''],
    [re.compile(' {0,1}<.*?>'), u''],
    [re.compile(' {0,1}/[A-Z]?/'), u''],
    [re.compile(' [A-Z,a-z]*?\+'), u''],
    [re.compile(' {0,1}\[.*?\]'), u''],
    [u'IDS: ', u''],
    [u'{', u''],
    [u'#', u''],
    [u'/', u''],
]
out = open("output/parlareitaliano_corpus_api.txt", "w", encoding="UTF-8")
final = ""
for link in soup.find_all('a'):
    href = link.get('href')
    if href.endswith(".hsw"):
        try:
            p = downloader.download_page("http://www.parlaritaliano.it"+href,decode="cp1252")
        except urllib.error.HTTPError as exc:
            print("error downloading",href,"error:",exc)
        else:
            text = clean_me.maybe_normalize(
                p, mapping=mapping_normalization, roman_normalization=False)
            if len(text) > 5: # TODO: parametrize?
                out.write(text+"\n")


out.close()
