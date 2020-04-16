import re
import os
import zipfile
from utils import sanitize, download


def parse(inp, out):
    # f.write(zfile.read(name))
    raw_lines = inp.splitlines()
    text = ""
    print("Found", len(raw_lines), "raw lines")
    for raw_line in raw_lines:
        try:
            line = raw_line.decode(encoding="cp1252")
        except UnicodeError as uex:
            pass
        else:
            if line.startswith("       "):
                text += line.strip() + "\n"
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
        [u'{', u''],
        [u'#', u''],
        [u'/', u''],

    ]
    text = clean_me.maybe_normalize(
        text, mapping=mapping_normalization, roman_normalization=False)
    text = clean_me.prepare_splitlines(text)

    final = ''
    nrLines = 0
    for l in text.splitlines():
        # print("line")
        # print(l)
        cleaned = clean_me.clean_single_line(l).strip()
        if len(cleaned) > 0:
            final += cleaned + "\n"
            nrLines += 1
    out.write(final)

    return nrLines


downloader = download.Download()
downloader = downloader.if_not_exist(
    'http://www.parlaritaliano.it/attachments/article/647/trascrizioni_ortografiche_(selezioni_da_tg_60s-05).zip')

out = open(os.path.join("output", "tg60s.txt"), "a", encoding="UTF-8")
with zipfile.ZipFile(downloader.file) as zfile:
    for name in zfile.namelist():
        if re.search("tg6[6-9]\.doc$", name):
            doc_name = name.split("/")[-1]
            print("Parsing", doc_name)
            nrLines = parse(zfile.read(name), out)
            print("Done with", doc_name, ". Nr of lines", nrLines)
out.close()
