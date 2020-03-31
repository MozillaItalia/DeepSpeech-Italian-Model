#!/usr/bin/env python3
import re
from utils import sanitize, line_rules, download

validate_line = line_rules.LineRules()
clean_me = sanitize.Sanitization()
download_me = download.Download()

mapping_normalization = [
    [u'_', u''],
    [u'-', u''],
    [u'—', u''],
    ['\n', u''],
    [u'*', u"\n"],
    [u'( ', u''],
    [u' , ', u', '],
    [u' )', u''],
    [u'<br/>', u"\n"],
    [u'<br>', u"\n"],
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
    [u':(', u''],
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
    ['  o  ', ''],
    [re.compile('(\s){2,}'), u' '],
    [re.compile('(\s){2,}$'), u' '],
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
raw_page = download_me.download_for_bp(HOME, 'ISO-8859-1')
lists = raw_page.find_all("ul")
# Getting the chat archives from homepage's anchors
anchors = lists[0].find_all("a")
pages = []
# List each href

for anchor in anchors:
    # Appending '_' to get a cleaner version of the page
    pages.append("_" + anchor["href"])

with open("./output/eulogos.txt", "w") as result:
    current = 0
    for page in pages:
        current += 1
        print("{}/{} pages".format(current, len(pages)))
        url = "{}/{}".format(HOME, page)
        print(url)
        soup = download_me.download_for_bp(url, 'ISO-8859-1')
        tables = soup.find_all("table")
        # Chat content is always in the 5th table
        rows = tables[4].find("tr")
        data_list = rows.find_all("td")
        for data in data_list:
            for raw_content in data.contents:
                text = ''
                raw_content = str(raw_content).strip()
                content = clean_me.maybe_normalize(raw_content, mapping_normalization)
                content = clean_me.prepare_splitlines(raw_content).splitlines()
                for line in content:
                    line = clean_me.clean_single_line(line)
                    if len(line) <= 12:
                        continue
                    
                    if len(line.split()) < 2:
                        continue
                    
                    if validate_line.isdigit([line, line[1:], line[:1]]):
                        continue
                    
                    if validate_line.contain(line, ['#', '/dcc', '•', 'http', '{', '(c)', 'antiflood', '`', 'ª', '[02]', '[03]', '[04]','^', ' n.', 'pp.']):
                        continue
        
                    if validate_line.startswith(line, ['(', '!', ')', '"', "'", "[", '-']):
                        continue
                    
                    if line.find("+") != -1 or line.isspace():
                        continue
                    
                    if not validate_line.parenthesismatch(line):
                        continue
                    
                    if validate_line.hasafinalrepeated(line):
                        continue
                    
                    text += line + "\n"
                    
                result.write(text)

result.close()

result = open('./output/eulogos.txt', 'r', encoding='utf-8')
print(' Number of lines: ' + str(len(result.read().splitlines())))
result.close()