#!/usr/bin/env python3
import os
import xml.etree.ElementTree as ET
from utils import sanitize, line_rules, download

# managing sanitizer
sanitizer = sanitize.Sanitization()

mapping_normalization = [
    [u'*', u''],
    [u'/', u''],
    [u'#', u''],
    [u'{', u''],
    [u'}', u''],
    [u'(', u''],
    [u')', u''],
    [u'[', u''],
    [u']', u'']
]

# managing parse directory name
parsedir = "parsing" + os.path.sep

# managing output pathname + output filename
outdir = "output" + os.path.sep
filename = "qallme.txt"

output_file = open(outdir + filename, "w", encoding='utf-8')

print("Qallme Importer")

download_link = 'http://qallme.fbk.eu/archive/QB_IT_V1.0_TranscriptionsReferences.zip'
downloader = download.Download()
downloader = downloader.if_not_exist(download_link)
downloader.zip_decompress(parsedir)

###  XML  ###
qallmef = ET.parse(parsedir + "QB_IT_V1.0_Translations/QallmebenchmarkIT_v1.0_final-translation.xml")
sentences = qallmef.findall("question/text")

# We are looking for sentences, not xml elements!
# turning xml elements into real sentences
for s in sentences:
    line = s.text
    if line is not None:
        line = sanitizer.maybe_normalize(line, mapping_normalization)
        output_file.write(line)
        output_file.write("\n")

output_file.close()
print("Import from QALLME completed!")
result = open(outdir + filename, 'r')
print(' Total lines: ' + str(len(result.read().splitlines())))
result.close()
