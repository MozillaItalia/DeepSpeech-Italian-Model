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
parsedir = "parsing/qall/"

# managing output pathname + output filename
output = "output/qallme.txt"

output_file = open(output, "w", encoding='utf-8')

print("Qallme Importer")

downloader = download.Download().if_not_exist('http://qallme.fbk.eu/archive/QB_IT_V1.0_TranscriptionsReferences.zip').zip_decompress(parsedir)

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
result = open(output, 'r')
print(' Total lines: ' + str(len(result.read().splitlines())))
result.close()
