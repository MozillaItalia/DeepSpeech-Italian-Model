#!/usr/bin/env python3
import sys, os, requests, time
import textract, string, re
from utils import sanitize

def download_and_merge_pdfs(urls):
    counter = 0

    for u in urls:
        # download and store pdf
        r = requests.get(u, allow_redirects=True)
        
        # check if pdf
        if r.headers.get('content-type') == "application/pdf":
            filename = str(counter) + ".pdf"

            # writes it
            open(filename, 'wb').write(r.content)
            
            # extract from pdf
            text = textract.process(filename).decode()

            # pdf to text
            open(str(counter) + ".txt", 'w').write(text)
        
        counter += 1


def remove_all(ext):
    """
        given an extension removes every file in the current directory
    """
    for f in os.listdir("."):
        if f.endswith("." + ext):
            os.remove(f)


def merge_txts():
    """
        merge every txt file into a temp file
    """

    # create and open the file in append
    fd = open(".." + os.path.sep + ".." + os.path.sep + "output" + os.path.sep + "temp.txt", "a")

    for f in os.listdir("."):
        if f.endswith(".txt"):
            fd.write(open(f, "r").read())

def has_numbers(inputString):
    return any(char.isdigit() for char in inputString)

def output_file():
    mapping_normalization = [
        [u'«', u''],
        [u'»', u''],
        [u'“', u''],
        [u'”', u''],
        [u'"', u''],
        [u'…', u''],
        [u'(', u''],
        [u')', u''],
        [u'[', u''],
        [u']', u''],
        [u'*', u''],
        [u';', u' '],
        [re.compile("\.\. "), u' '],
        [re.compile("Chiara Lubich: "), u''],
        [re.compile("Chiara, "), u''],
        [re.compile("Chiara: "), u''],
        [re.compile("Chiara: "), u''],
        [re.compile("Dio, "), u''],
        
        [re.compile("([cC]')[eE]'"), u'\g<1>è'],
        [re.compile("É "), u'è '],
    ]

    sanitizer = sanitize.Sanitization()

    # open temp file
    content = open("output" + os.path.sep + "temp.txt", "r").readlines()
    
    # sort everything and strip new line
    content = sorted(list(set([ c.strip() for c in content ])))
    
    frasi = []

    for c in content:
        # writes only if there are not numbers in the sentence
        if not has_numbers(c):
            c = sanitizer.maybe_normalize(c, mapping=mapping_normalization, roman_normalization=False, mapping_prepend=True)
            c = sanitizer.clean_single_line(c)
            
            # not null and len between 13 and 120
            if c != "" and len(c) >= 13 and len(c) <= 120:
                c = remove_point_if_not_there(c)    # to avoid double sentences 
                frasi.append(c)
            
    # sort the sentences for better 
    frasi = sorted(list(set(frasi)))

    final = open("output" + os.path.sep + "lubich_importer.txt", "a")

    for f in frasi:
        final.write(f)
        final.write("\n")
    
    os.remove("output" + os.path.sep + "temp.txt")
    

def remove_point_if_not_there(s:str):
    return (s[0:-1]) if s[-1] in [".", "?", ",", "!"] else s
         

def main():
    # to calculate time elapsed later
    start_time = time.time()
    
    print("Lubich Importer")

    # create parse and json folders
    parsefolder = "parsing" + os.path.sep
    if not os.path.exists(parsefolder):
        os.mkdir(parsefolder)

    pdf_folder = parsefolder + "PDF"
    if not os.path.exists(pdf_folder):
        os.mkdir(pdf_folder)

    # creating folder for output
    outfolder = "output"
    outfilepath = outfolder + os.path.sep + "temp.txt"

    # retrieving urls
    fd = open("assets" + os.path.sep + "lubich_urls.txt", "r")
    urls = fd.readlines()

    urls = [ url.strip() for url in urls ]

    # moving into pdf directory
    os.chdir(parsefolder + os.path.sep + "PDF")

    # downloading everything in pdf
    download_and_merge_pdfs(urls)

    # merging txts from pdfs
    merge_txts()

    remove_all("pdf")
    remove_all("txt")

    # returning back to the main folder
    os.chdir("../../")

    # build output file in output/lubich_importer.txt
    output_file()

    print("Import from lubich archive completed!")
    print("Time elapsed: " + str(int(int(time.time() - start_time) / 60)) + " minutes")


main()
