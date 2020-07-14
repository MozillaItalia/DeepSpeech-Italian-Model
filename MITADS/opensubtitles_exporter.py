#!/usr/bin/env python3

import re
from pathlib import Path
from unidecode import unidecode
from utils import sanitize, line_rules, download
from concurrent.futures import ProcessPoolExecutor
from xml.dom import minidom

start_year = 1920
output_file = './output/opensubtitles_'

download_me = download.Download()
validate_line = line_rules.LineRules()
clean_me = sanitize.Sanitization()

# Custom packaging instead of the official one of 5,8gb in zip
# This tar.bz2 version is 960mb but with the same content
folder_dataset = download_me.if_not_exist('https://codeat.owncube.com/index.php/s/os3XjRXBWdBAd7H/download').tarbz2_decompress('./parsing/opensubtitles/')

mapping_normalization = [
    # If the sentence start with a number, the sentence is removed
    [re.compile('^\d+(.*)'), u''],

    # Remove the stuff inside ()[]{}
    [re.compile('(\(|\[|{)[^(\)|\]|})]*(\)|\]|})'), u''],
    # must be twice time for nested parentheses
    [re.compile('(\(|\[|{)[^(\)|\]|})]*(\)|\]|})'), u''],

    # remove uninteresting characters
    [re.compile('\-|=|_|–|\+|\(|\||—|\)|\[|\]|~|\*|/|"|¨|\^'), u' '],

    # Sanitize ... to .
    [re.compile('\.+'), u'.'],

    # accentate maiuscole
    [re.compile('È'), u'e\''],

    # Sanitize single apex
    [re.compile('´|`|\'\''), u'\''],

    # To avoid conflicts with single ' and accented letter we removed them
    [re.compile('(\s|^)(\')([^\']*)(\')(\s|$)'), r'\3'],

    # remove char for those cases
    [re.compile('(#\d+)|#|(\s°)'), u''],

    # Sanitization for those cases
    [u'n°', u'numero '],

    # Sanitization for currency values
    [re.compile('\$\s*([0-9]+[.,]{0,1}[0-9]*)'), r'\1 dollari'],
    [re.compile('([0-9]+[.,]{0,1}[0-9]*)\s*\$'), r'\1 dollari'],
    [re.compile('(₤|£)\s*([0-9]+[.,]{0,1}[0-9]*)'), r'\2 lire'],
    [re.compile('([0-9]+[.,]{0,1}[0-9]*)\s*₤'), r'\1 lire'],
    [re.compile('(€)\s*([0-9]+[.,]{0,1}[0-9]*)'), r'\2 euro'],
    [re.compile('([0-9]+[.,]{0,1}[0-9]*)\s*€'), r'\1 euro'],
    [u'¢', u'c'],
]

mapping_normalization_after_decode = [
    # Convert old fashion accented letter to the real accented letter
    [u'E\' ', u'è '],
    [re.compile('a\'(\s|$|,|\.|\?)'), r'à\1'],
    [re.compile('e\'(\s|$|,|\.|\?)'), r'è\1'],
    [re.compile('i\'(\s|$|,|\.|\?)'), r'ì\1'],
    [re.compile('o\'(\s|$|,|\.|\?)'), r'ò\1'],
    [re.compile('u\'(\s|$|,|\.|\?)'), r'ù\1'],
]

def parsexmlfile(path_info):
    count_file, xml_path = path_info
    xml_path = str(xml_path)

    result = open( output_file + str(count_file) + '.txt', 'w' )
    mydoc = minidom.parse(xml_path)
    items = mydoc.getElementsByTagName('s')

    # build the sentence/text
    text = ''
    for elem in items:
        words = elem.getElementsByTagName("w")
        for word in words:
            if word.firstChild.data != '':
                text += word.firstChild.data + ' '

        text += "\n"

    text = clean_me.maybe_normalize(
        text.strip(), mapping_normalization, roman_normalization=False)

    # Opensubtiles Dataset contains no-ASCII char
    #  we use unidecode to delegate all unicode char processing
    #  to keep all vowels properly accented, and at the same time eliminate the other unicode characters,
    #  you need to use a substitution with place holders
    text = text.replace('à', '<PH_A>')
    text = text.replace('è', '<PH_E>')
    text = text.replace('ì', '<PH_I>')
    text = text.replace('ò', '<PH_O>')
    text = text.replace('ù', '<PH_U>')
    text = unidecode(text)
    text = text.replace('<PH_A>','à')
    text = text.replace('<PH_E>','è')
    text = text.replace('<PH_I>','ì')
    text = text.replace('<PH_O>','ò')
    text = text.replace('<PH_U>','ù')
    text = clean_me.maybe_normalize(
        text, mapping_normalization_after_decode, roman_normalization=False)

    lines = clean_me.prepare_splitlines(text).splitlines()
    for line in lines:
      line = clean_me.clean_single_line(line).strip()

      if len(line) <= 2:
          continue

      if validate_line.contain(line, ['®', '{', '}', '©', '±', '_', '@', '+', ':']):
          continue

      text += line + "\n"

    result.write(text)
    result.close()

    return len(lines)

def get_year(path): return int(str(path.parent.parent._parts[len(path.parent.parent._parts)-1]))

def main():
    print(' Parsing in progress')
    pathlist = (folder_dataset / Path('OpenSubtitles/xml/it/')).glob('**/*.xml')
    paths = filter(lambda x: get_year(x) > start_year, pathlist)
    with ProcessPoolExecutor() as pool:
        lines = pool.map(parsexmlfile, enumerate(paths))
        total_lines = sum(lines)

    print(' Total lines ' + str(total_lines))

main()
