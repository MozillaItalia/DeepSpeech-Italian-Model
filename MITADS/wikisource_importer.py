#!/usr/bin/env python3
from urllib.request import Request, urlopen
from fake_useragent import UserAgent
from utils import sanitize, line_rules

validate_line = line_rules.LineRules()
clean_me = sanitize.Sanitization()


books = open( './assets/wikisource_books.txt', 'r' ).read().splitlines()
start = 1
download_link = 'https://tools.wmflabs.org/wsexport/tool/book.php?lang=it&format=txt&page='
result = open("./output/wikisource.txt", "w", encoding='utf-8')
print("Number of books to import: {}".format(len(books)))

ua = UserAgent()

for book in books:
    print("Processing book : {}\n {} of {}".format(book,start,len(books)))
    response = Request(download_link + book, headers={'User-Agent': ua.random})
    data = urlopen(response).read().decode('UTF-8')

    raw_text = clean_me.maybe_normalize(data.strip())
    raw_text = clean_me.splitlines(raw_text).splitlines()
    
    text = ''
    for sentences in raw_text:
        lines = sentences.split(".")
        for line in lines:
            line = clean_me.cleansingleline(line).strip()
            if len(line) <= 12:
                continue
            
            if line.isupper():
                continue
            
            if line == 'creativecommons':
                continue
            
            if validate_line.contain(line, ['Â§', '=', '--', '~', 'wiki', 'licenses', '//', ' pp', ' Ibid', '■', '^']):
                continue
            
            if line.find('/') >= 1:
                continue
            
            if validate_line.brokenparenthesis(line):
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
print('Number of lines: ' + str(len(result.read().splitlines())))
result.close()
