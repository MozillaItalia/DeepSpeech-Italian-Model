#!/usr/bin/env python3
from utils import sanitize, line_rules, download
import time

validate_line = line_rules.LineRules()
clean_me = sanitize.Sanitization()
download_me = download.Download()

books = open( './assets/wikisource_books.txt', 'r' ).read().splitlines()
start = 1
download_link = 'https://tools.wmflabs.org/wsexport/tool/book.php?lang=it&format=txt&page='
result = open("./output/wikisource.txt", "w", encoding='utf-8')
print(" Number of books to import: {}".format(len(books)))


for book in books:
    time.sleep(5)
    print("  Processing book : {}\n   {} of {}".format(book,start,len(books)))
    raw_text = download_me.downloadpage(download_link + book)
    raw_text = clean_me.maybe_normalize(raw_text)
    raw_text = clean_me.preparesplitlines(raw_text).splitlines()
    
    text = ''
    for sentences in raw_text:
        lines = sentences.split(".")
        for line in lines:
            line = clean_me.cleansingleline(line).strip()
            if len(line) <= 12:
                continue
            
            if line == 'creativecommons':
                continue
            
            if validate_line.contain(line, ['§', '=', '--', '~', 'wiki', 'licenses', '//', ' pp', ' Ibid', '■', '^']):
                continue
            
            if line.find('/') >= 1:
                continue
            
            if validate_line.isbrokenparenthesis(line):
                continue

            if validate_line.startswith(line, ['(', '...', ',', '[']):
                continue
            
            if validate_line.endswith(line, [' M', ' p', 'n', ' F', ' D', ' T', ' N']):
                continue
            
            if validate_line.isdigit([line, line[1:], line[:1]]):
                continue
            
            if validate_line.isbookref(line):
                continue
                
            if validate_line.isbrokensimplebracket(line):
                continue
            
            text += line + "\n"
            
    result.write(text)
    start += 1
    
result.close()

result = open('./output/wikisource.txt', 'r', encoding='utf-8')
print(' Number of lines: ' + str(len(result.read().splitlines())))
result.close()
