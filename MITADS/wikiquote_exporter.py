#!/usr/bin/env python3
from typing import Iterator
import itertools
from multiprocessing import Pool
from xml.dom import minidom
from html import unescape
import re
from utils import sanitize, line_rules, download

# ideas of stuff that can be done:
# create a line class that handles validation as well
# for now define Lines type
Lines = Iterator[str]

DOWNLOAD_PATH = 'https://dumps.wikimedia.org/itwikiquote/latest/itwikiquote-latest-pages-articles.xml.bz2'
OUTFILE = "output/wikiquote.txt"

download_me = download.Download()
validate_line = line_rules.LineRules()
clean_me = sanitize.Sanitization()

sub_regex = re.compile(r"""\[\[(File|Category):[\s\S]+\]\]|
                        \[\[[^|^\]]+\||
                        \[\[|\]\]|
                        \'{2,5}|
                        (<s>|<!--)[\s\S]+(</s>|-->)|
                        (<s>|<!)[\s\S]+(</s>|>)|
                        {{[\s\S\n]+?}}|
                        <.*?>|
                        ={1,6}""", re.VERBOSE)

normalize_rules = [['*', u"\n"],
                   ['<br />', u"\n"],
                   ['<br>', u"\n"],
                   ["\(\d\d\d\d\)", ""],
                   ["[\(\[].*?[\)\]]", ""],
                   ['AvvertenzaContattiDonazioni', '']
                   ]


def get_elements():
    """ returns an iterable of the item that needs to be processed: nodes od the xml document"""
    xml = download_me.if_not_exist(DOWNLOAD_PATH).bz2_decompress()
    doc = minidom.parse(xml)
    return doc.getElementsByTagName('page')


def process_element(elem) -> Lines:
    """ elem is a child of the wikiquote xml, returns and iterable of lines, None if the element cannot be processed"""
    title = elem.getElementsByTagName("title")[0].firstChild.data
    # check that this line is valid
    if 'wiki' in title and title == 'Pagina principale' and 'MediaWiki' in title:
        return None
    textdom = elem.getElementsByTagName("revision")[0].getElementsByTagName("text")[0]

    if textdom.firstChild is None: return None

    lines = clean_split_text(textdom.firstChild.data)
    # split and strip lines
    lines = map(clean_me.clean_single_line, lines)
    lines = map(lambda x: x.strip(), lines)
    return list(filter(line_filter, lines))


def clean_split_text(text):
    text = unescape(text)
    text = sub_regex.sub("", text)
    text = clean_me.maybe_normalize(text, normalize_rules, False)
    return clean_me.prepare_splitlines(text).splitlines()


def line_filter(line):
    """checks if line is invalid"""
    if (validate_line.startswith(line, ['(', 'vivente)']) or
            validate_line.contain(line, ['|', '{', '}', ':', '[', 'ISBN', '#', 'REDIRECT', 'isbn', 'RINVIA']) or
            validate_line.isdigit([line, line[1:], line[:1]]) or
            validate_line.isbookref(line) or
            validate_line.isbrokensimplebracket(line)):
        return False
    else:
        return True


def multiprocess_runner(processor, items):
    with Pool() as pool:
        return pool.map(processor, items)


def runner(processor, items):
    return map(processor, items)


def write_results(results, filename):
    """result is a list of list of valid lines"""
    with open(filename, 'w') as f:
        for lines in results:
            if lines:
                # write lines filtering out None lines
                lines = filter(lambda x: bool(x), lines)
                f.writelines(itertools.chain.from_iterable(zip(lines, itertools.repeat("\n"))))


def main():
    print("Starting wikiquote")
    items = get_elements()
    print("finished init")
    write_results(runner(process_element, items), OUTFILE)
    print("Done!")


if __name__ == "__main__":
    main()
