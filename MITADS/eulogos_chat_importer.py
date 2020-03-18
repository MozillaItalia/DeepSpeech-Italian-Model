#!/usr/bin/env python3
import re
import requests
import roman
from typing import Pattern
from bs4 import BeautifulSoup, Tag, NavigableString


def get_page_content(url):
    headers = requests.utils.default_headers()
    headers.update({'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:74.0) Gecko/20100101 Firefox/74.0', 'Content-Type': 'text/html; charset=utf-8'})
    raw_page = requests.get(url, headers)
    return BeautifulSoup(raw_page.content, 'html.parser')


def extract_content(scraped):
    if isinstance(scraped, Tag):
        return scraped.prettify().splitlines()
    elif isinstance(scraped, NavigableString):
        return scraped.splitlines()
    else:
        print("UNHANDLED TYPE: {}".format(type(scraped)))


def getRomanNumbers(ch):
    ROMAN_CHARS = "XVI"
    ro = ''
    ros = 0
    for i in range(len(ch)):
        c = ch[i]
        if c in ROMAN_CHARS:
            if len(ro) == 0 and not ch[i - 1].isalpha():
                ro = c
                ros = i
            else:
                if len(ro) > 0 and ch[i - 1] in ROMAN_CHARS:
                    ro += c
        else:
            if len(ro) > 0:
                if not c.isalpha():
                    yield ch[ros - 1], ch[i], ro
                ro = ''
                ros = i
    if len(ro) > 0:
        yield ch[ros - 1], '', ro


def parenthesis_match(text):
    last = None
    for char in text:
        if char == '(':
            if last is None or last == ')':
                last = char
            elif last == '(':
                return False
        elif char == ')':
            if last == '(':
                last = char
            elif last is None or last == ')':
                return False
    return True

def maybe_normalize(value, mapping):
    for norm in mapping:
        if type(norm[0]) == str:
            value = value.replace(norm[0], norm[1])
        elif isinstance(norm[0], Pattern):
            value = norm[0].sub(norm[1], value)
        else:
            print('UNEXPECTED', type(norm[0]), norm[0])
    for ro_before, ro_after, ro in getRomanNumbers(value):
        try:
            value = value.replace(ro_before + ro + ro_after, ro_before + str(roman.fromRoman(ro)) + ro_after)
        except roman.InvalidRomanNumeralError as ex:
            print(ex)
            pass
    if value.startswith(';'):
        value = value[1:]
    return value.replace('  ', " ")


def main():
    mapping_normalization = [
        [u'«', u''],
        [u'»', u''],
        [u'×', u''],
        [u'_', u''],
        [u'-', u''],
        [u'—', u''],
        ['\n', u''],
        [u'* * * ', u''],
        [u'*', u"\n"],
        [u'( ', u''],
        [u' , ', u', '],
        [u' )', u''],
        [u'<br/>', u"\n"],
        [u'<br>', u"\n"],
        [u'Sig. ', u'Signor '],
        [u'[', u''],
        [u']', u''],
        [u'<', u''],
        [u'>', u''],
        [u'{', u''],
        [u'}', u''],
        [u'^', u''],
        [u':)', u''],
        [u':D', u''],
        [u':P', u''],
        [u':O', u''],
        [u';)', u''],
        [u'§', u''],
        [u'¤', u''],
        [u'\\', u''],
        [u'º', u''],
        [u'°', u''],
        [u'|', u''],
        [u'/', u''],
        [u'#', u''],
        [u'¿', u''],
        [u'@', u''],
        [u'=', u''],

        [re.compile('^[\W_]+$'), u''],
        [re.compile('[.]'), u''],
        # remove nicknames
        [re.compile('^\s*(\w+\s*:)'), u''],
        # removes words written with digits & letters (ex: c1a0)
        [re.compile('([A-Za-z]+\d+).*'), u''],
        [re.compile('!{2,}'), u'!'],
        [re.compile('\?{2,}'), u'?'],
        [re.compile('\){2,}'), u''],
        [re.compile('\({2,}'), u''],
        [re.compile('^((?![A-Za-z]).)*$'), u''],
        [re.compile('\s*:$'), u''],

    ]
    HOME = "http://www.intratext.com/IXT/ITA0192"
    soup = get_page_content(HOME)
    lists = soup.find_all("ul")
    # Getting the chat archives from homepage's anchors
    anchors = lists[0].find_all("a")
    pages = []
    # List each href

    for anchor in anchors:
        # Appending '_' to get a cleaner version of the page
        pages.append("_" + anchor["href"])

    with open("output.txt", "w") as out:
        current = 0
        for page in pages:
            current += 1
            print("{}/{} pages".format(current, len(pages)))
            url = "{}/{}".format(HOME, page)
            soup = get_page_content(url)
            tables = soup.find_all("table")
            # Chat content is always in the 5th table
            rows = tables[4].find("tr")
            data_list = rows.find_all("td")
            i = 0
            for data in data_list:
                for raw_content in data.contents:
                    content = extract_content(raw_content)
                    for line in content:
                        cleaned = maybe_normalize(line.strip(), mapping_normalization)
                        if len(cleaned) <= 15:
                            continue
                        if len(cleaned.split()) < 2:
                            continue
                        if cleaned.strip().isdigit() or cleaned.strip().isnumeric():
                            continue
                        i += 1
                        if cleaned.find('`') != -1 or cleaned.find('¨') != -1 or cleaned.find('ms') != -1:
                            continue
                        if cleaned.strip().strip().startswith('!') or cleaned.strip().startswith('(') or cleaned.strip().startswith('"') or cleaned.strip().startswith("'"):
                            continue
                        if cleaned.find("+") != -1 or cleaned.isspace():
                            continue
                        if not parenthesis_match(cleaned):
                            continue

                        out.write(cleaned + "\n")


if __name__ == "__main__":
    main()
