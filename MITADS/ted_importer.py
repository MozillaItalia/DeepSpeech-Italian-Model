#!/usr/bin/env python3
# TODO: check if any other talk contains italian subs, for now just italian talks are managed
from bs4 import BeautifulSoup
from utils import sanitize
import requests
import re
import json
import time
import os

def main():
    # to calculate time elapsed later
    start_time = time.time()

    # create parse and json folders
    parsefolder = "parsing" + os.path.sep
    if not os.path.exists(parsefolder):
        os.mkdir(parsefolder)
        trace(parsefolder + " created!")

    jsonfolder = parsefolder + "JSON"
    if not os.path.exists(jsonfolder):
        os.mkdir(jsonfolder)
        trace(jsonfolder + " created!")

    # creating folder for output
    outfolder = "output"
    outfilepath = outfolder + os.path.sep + "ted_importer.txt"

    # cleaning output file -> to truncate a file open in write mode with plus
    fh_out = open(outfilepath, "w+")
    fh_out.close()

    # cleaning log file
    clean_log()

    # managing beautifulsoup res
    baseurl = "https://www.ted.com"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}

    pagenumber = 1
    file_counter = 0

    print("TedImporter")
    
    the_end = False
    while(not the_end):
        # request the page related to talks
        req = requests.get(baseurl + "/talks?language=it&page=" +
                           str(pagenumber), headers=headers, timeout=5)

        data = req.text  # contiene tutta la pagina
        soup = BeautifulSoup(data, 'lxml')  # ho estratto l'html

        # check whether i am at the end or not:
        # we are not at the end if this particular div
        # is not encountered
        div = soup.find("div", {"class": "h3 m2"})

        if(div is None):
            # the page exists
            # all our links are under class col
            divs = soup.find_all(class_='col')

            # LOG: update log file
            trace("Page number: " + str(pagenumber))

            for div in divs:
                # search all the links who contains potential json data
                a_links = div.find_all(
                    'a', {"class": "ga-link", "data-ga-context": "talks"}, href=True)

                for a in a_links:
                    if(a.string is not None):   # if we are not treating an empty link
                        manage_json_from_a(
                            a, baseurl, headers, jsonfolder, outfilepath)

                    file_counter += 1

            pagenumber += 1
        else:
            the_end = True

    print("Import from ted.com completed!")
    print("Time elapsed: " + str( int( int( time.time() - start_time ) / 60 ) ) + " minutes" )

    trace("Created and parsed " + str(file_counter) + " files.")

def manage_json_from_a(a, baseurl, headers, jsonfolder, outfilepath):
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
        [u']', u''],
        [u'Sig ', u'Signor '],
        [u'Sr ', u'Signor '],
        [u'Sra ', u'Signora '],
        [u'Mr', u'Signor'],
        [u'Miss', u'Signor'],
        [u'Mrs', u'Signora'],
        [u'<i>', u'']   # because there are these strange tags
    ]

    imported = False

    # take the name and the url from the a link
    name = a['href'].split("/")[2].split("?")[0]
    url = a['href'].split("?")[0]

    # retrieve json
    url = baseurl + url + "/transcript.json?language=it"

    trace("Retrieving JSON for : " + url)

    while(not imported):    # because we may encounter in an error
        try:
            r = requests.get(url, headers=headers, timeout=5)

            if(r.status_code == 200):
                json_path_file = jsonfolder + os.path.sep + name + ".json"

                # check file
                if os.path.isfile(json_path_file):
                    trace("File exists! Skipping creating new file...")
                else:
                    open(json_path_file, 'wb').write(r.content)
                    trace("Creating json file: " + name)
        
                # parse json file 
                write_sentences(clean_sentences(get_raw_sentences(name + ".json", jsonfolder), sanitizer, mapping_normalization), outfilepath)
                trace("Writing...")
            
                imported = True
            else:
                if(r.status_code == "429"):
                    trace("Timeout error: " +
                          str(r.status_code))
                else:   # any other error
                    trace(str(r.status_code) + " ERROR! The hamster fell off the wheel! Trying again...")
        except Exception as e:
            print(e)
            # if any exception is triggered (for example, connection closed)
            trace("ERROR! (Exception) The hamster fell off the wheel! Trying again...")

'''
    parse all json which are inside jsonfolder
    
    INCLUDED JUST FOR DEBUG PURPOSE (ex. testing just the JSON import if every json file has been downloaded)
'''
def parse_all_json():
    # create parse and json folders
    parsefolder = "parsing" + os.path.sep
    if not os.path.exists(parsefolder):
        os.mkdir(parsefolder)

    jsonfolder = parsefolder + "JSON"
    if not os.path.exists(jsonfolder):
        os.mkdir(jsonfolder)

    outfolder = "output"
    outfilepath = outfolder + os.path.sep + "ted_importer.txt"

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
        [u']', u''],
        [u'Sig ', u'Signor '],
        [u'Sr ', u'Signor '],
        [u'Sra ', u'Signora '],
        [u'<i>', u'']
    ]
    
    # cycling our JSON files
    for f in os.listdir(jsonfolder):
        write_sentences(clean_sentences(get_raw_sentences(f, jsonfolder), sanitizer, mapping_normalization), outfilepath)

        
'''
    given sentences (all in one line), sanitizer and a mapping
    return a list of cleaned sentences
'''
def clean_sentences(raw_sentences, sanitizer, mapping_normalization):
    sentences_list = []

    # custom sanitizer: this should replace all
    # carriages return with ''
    # otherwise sentences are broken while sanitizing
    raw_sentences = raw_sentences.replace("\n", " ")

    # another custom sanitizer: this allow us
    # to remove full stop inside numbers
    raw_sentences = re.sub("([0-9]).([0-9])", r"\1\2", raw_sentences)

    # list of sentences by using regex, because of special punctuation
    sentences = re.split(r'[."?!]\s*', raw_sentences)
    
    for s in sentences:
        if(s is not None and len(s) >= 10):
            sentences_list.append(sanitizer.maybe_normalize(s, mapping_normalization))

    return sentences_list


'''
    given a json, return a group of sentences
'''
def get_raw_sentences(json_file_name, jsonfolder):
    trace("Parsing: " + json_file_name)

    raw_sentences = ""

    # loading json data
    filehl = open(jsonfolder + os.path.sep + json_file_name, 'r')
    json_data = (json.loads(filehl.read()))

    # effectively parsing JSON
    for paragraph in json_data['paragraphs']:
        for cues in paragraph['cues']:
            raw_sentences += " " + cues['text']

    return raw_sentences


'''
    write a group of sentences into a file
    @params: sentences, outfilepath
'''
def write_sentences(sentences, outfilepath):
    outfile_hl = open(outfilepath, 'a+')

    for s in sentences:
        outfile_hl.write(s + "\n")

        trace("[" + str(len(s)) + "]" + s)

    outfile_hl.close()


'''
    write a string in a log_file
'''
def trace(string):
    parsefolder = "parsing"
    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)

    fh = open(parsefolder + os.path.sep + "ted_log.txt", "a+")

    fh.write(current_time + " : " + str(string) + "\n")
    fh.close()


'''
    clean log file
'''
def clean_log():
    parsefolder = "parsing"
    fh = open(parsefolder + os.path.sep + "ted_log.txt", "w+")
    fh.close()


main()
