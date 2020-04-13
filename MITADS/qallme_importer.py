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

# print("\n")
print("Qallme Importer")
print("===============")
# downloading resource
download_link = 'http://qallme.fbk.eu/archive/QB_IT_V1.0_TranscriptionsReferences.zip'

downloader = download.Download()
downloader = downloader.if_not_exist(download_link)

# extracting files
downloader.zip_decompress(parsedir)

# going to the right directory
os.chdir(parsedir + "QB_IT_V1.0_Translations")  # name of the folder inside
                                                # the zip package


###  XML  ###
qallmef = ET.parse("QallmebenchmarkIT_v1.0_final-translation.xml")

sentences = qallmef.findall("question/text")
len_sentences = len(sentences)

print("Now parsing " + str(len_sentences) + " sentences... ")

# We are looking for sentences, not xml elements!
# turning xml elements into real sentences
i = 0
for s in sentences:
    sentences[i] = sentences[i].text
    i += 1

# sanitizing line by using libs
for line in sentences:    
    if line is not None:    # if we are not treating an empty line
        line = sanitizer.maybe_normalize(line, mapping_normalization)

# print("OK!")


print("Now writing to " + outdir + filename + "... ")

# writing to output file
for line in sentences:
    if line is not None:
        output_file.write(line)
        output_file.write("\n")

#print("OK!\n")

print("Import from QALLME completed!")
