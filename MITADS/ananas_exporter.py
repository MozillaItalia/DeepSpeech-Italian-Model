#!/usr/bin/env python3
import re
import os
import zipfile
from utils import sanitize, download

# start downloading ITALIANO.ZIP
downloader = download.Download()
downloader = downloader.if_not_exist(
    'http://www.parlaritaliano.it/attachments/article/716/ITALIANO.zip')
with zipfile.ZipFile(downloader.file) as italiano:
    with italiano.open('ITALIANO/ITALIANO_TRASCRIZIONI.zip') as trascrizioni:
        with zipfile.ZipFile(trascrizioni) as trascrizioni_ita:
            trascrizioni_ita.extractall(path=downloader.folder)

downloader = downloader.if_not_exist(
    'http://www.parlaritaliano.it/attachments/article/644/PALERMO.zip')
with zipfile.ZipFile(downloader.file) as palermo:
    with open(os.path.join(downloader.folder,"ITALIANO_TRASCRIZIONI","palermo.txt"), 'wb') as f:
        f.write(palermo.read('PALERMO/corpusPa/DGmtB03P.txt'))

downloader = downloader.if_not_exist(
    'http://www.parlaritaliano.it/attachments/article/644/ROMA.zip')
with zipfile.ZipFile(downloader.file) as palermo:
    with open(os.path.join(downloader.folder,"ITALIANO_TRASCRIZIONI","roma.txt"), 'wb') as f:
        f.write(palermo.read('ROMA/corpusRm/DGtdB04R.txt'))

clean_me = sanitize.Sanitization()

mapping_normalization = [
    [u'/', u''],
    [u'#', u''],
    [u'{', u''],
    [u'}', u''],
    [u'*ciailecca', u'cilecca'],  # a very custom one
    [re.compile('<.*?>'), u''],
    [re.compile('\*[a-z,A-Z]*#'), u''],
    [re.compile('\[.*?\]'), u''],
    [re.compile('\{.*?\}'), u''],
    [re.compile('p.*:'), u''],
    [re.compile("[a-z]*\+\s{0,1}#{0,1}"), u''],
    ["[", u''],
    ["]", u''],
    [re.compile("[Ww]hisp[a-z]+"), u''],
]
texts_dir = os.path.join(downloader.folder, "ITALIANO_TRASCRIZIONI")
result = open('./output/ananas.txt', 'w', encoding="UTF-8")
final = ''
for t in os.listdir(texts_dir):
    print("Parsing",t,"...")
    raw_text = open(os.path.join(texts_dir, t), 'r',
                    encoding="ISO-8859-15").read()
    # avoid hard sentence splitting
    raw_text = re.sub(r"\n +(.)", r" \g<1>", raw_text)
    raw_text_lines = raw_text.splitlines()
    text = ''
    for line in raw_text_lines:
        if line.startswith('p'):
            text += line + "\n" if len(line) > 2 else ""
    text = clean_me.maybe_normalize(text, mapping=mapping_normalization)
    for l in text.splitlines():
        cleaned = clean_me.clean_single_line(l).strip()
        if len(cleaned) > 0:
            final += cleaned + "\n"

    print("Done!")
result.write(final)
result.close()
output_file = './output/ananas.txt'
result = open(output_file, 'r')
print(' Total lines: ' + str(len(result.read().splitlines())))
result.close()
print("Parsing done. Text file saved in", output_file)
