#!/usr/bin/env python3
from utils import sanitize, line_rules, download
import time

OUTFILE = "output/wikisource.txt"
DISCARD_FILE = 'output/discarded/wikisource.json'
DOWNLOAD_LINK = 'https://wsexport.wmflabs.org/tool/book.php?lang=it&format=txt&page='

validate_line = line_rules.LineRules(DISCARD_FILE)
clean_me = sanitize.Sanitization()
download_me = download.Download()


def process_line(line, out_file):
    """if line is invalid returns early, if is correct writes the line to the file"""
    line = clean_me.clean_single_line(line)
    if (validate_line.is_not_valid(line) or
        len(line) <= 12 or
        line == 'creativecommons' or
        validate_line.contain(line, ['§', '=', '--', '~', 'wiki', 'licenses', '//', ' pp', ' Ibid', '■', '^']) or
        # line.find('/') >= 1 or  or commented out because with the current regex digits and brackets are always discarded
        validate_line.isbrokenparenthesis(line) or
        validate_line.startswith(line, ['(', '...', ',', '[']) or
        validate_line.endswith(line, [' M', ' p', 'n', ' F', ' D', ' T', ' N']) or
        # validate_line.isdigit([line, line[1:], line[:1]]) or commented out because with the current regex digits and brackets are always discarded
        validate_line.isbookref(line) ):
        # validate_line.isbrokensimplebracket(line)):  or commented out because with the current regex digits and brackets are always discarded
        return False
    else:
        out_file.write(line + "\n")
        return True


def process_book(book, out_file):
    raw_text = download_me.download_page(DOWNLOAD_LINK + book)
    raw_text = clean_me.maybe_normalize(raw_text)
    raw_text = clean_me.prepare_splitlines(raw_text).splitlines()
    tot_lines = 0
    for sentences in raw_text:
        for line in sentences.split("."):
             if process_line(line, out_file): tot_lines += 1

    return tot_lines


def main():
    books = open('./assets/wikisource_books.txt', 'r').read().splitlines()
    result = open(OUTFILE, "w", encoding='utf-8')
    print(" Number of books to import: {}".format(len(books)))

    tot_lines = 0
    for count, book in enumerate(books):
        time.sleep(5) # to avoid being banned from wikipedia servers for excess in requests
        print("  Processing book : {}\n   {} of {}".format(book, count, len(books)))
        tot_lines += process_book(book, result)

    result.close()

if __name__ == '__main__':
    main()