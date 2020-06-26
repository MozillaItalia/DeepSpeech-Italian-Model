#!/usr/bin/env python3
# TODO: check if any other talk contains italian subs, for now just italian talks are managed
from bs4 import BeautifulSoup
from utils import sanitize
import requests
import re
import json
import time
import os

# managing sanitizer
sanitizer = sanitize.Sanitization()


def main():
    # to calculate time elapsed later
    start_time = time.time()

    # create parse and json folders
    parsefolder = "parsing" + os.path.sep
    if not os.path.exists(parsefolder):
        os.mkdir(parsefolder)

    jsonfolder = parsefolder + "JSON"
    if not os.path.exists(jsonfolder):
        os.mkdir(jsonfolder)

    # creating folder for output
    outfolder = "output"
    outfilepath = outfolder + os.path.sep + "ted_importer.txt"

    # cleaning output file -> to truncate a file open in write mode with plus
    fh_out = open(outfilepath, "w+")
    fh_out.close()

    # cleaning log file
    #clean_log()

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
        req = requests.get(baseurl + "/talks?language=it&page="
                           + str(pagenumber), headers=headers, timeout=5)

        data = req.text  # contiene tutta la pagina
        #soup = BeautifulSoup(data, 'lxml')
        soup = BeautifulSoup(data, 'html.parser')  # ho estratto l'html

        # check whether i am at the end or not:
        # we are not at the end if this particular div
        # is not encountered
        div = soup.find("div", {"class": "h3 m2"})

        if(div is None):
            # the page exists
            # all our links are under class col
            divs = soup.find_all(class_='col')

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
    print("Time elapsed: " + str(int(int(time.time() - start_time) / 60)) + " minutes")


def manage_json_from_a(a, baseurl, headers, jsonfolder, outfilepath):

    imported = False

    # take the name and the url from the a link
    name = a['href'].split("/")[2].split("?")[0]
    url = a['href'].split("?")[0]

    # retrieve json
    url = baseurl + url + "/transcript.json?language=it"

    while(not imported):    # because we may encounter in an error
        try:
            r = requests.get(url, headers=headers, timeout=5)

            if(r.status_code == 200):
                json_path_file = jsonfolder + os.path.sep + name + ".json"

                # check file
                if not os.path.isfile(json_path_file):
                    json_file = open(json_path_file, 'wb')
                    json_file.write(r.content)
                    json_file.close()

                # parse json file
                write_sentences(clean_sentences(get_raw_sentences(
                    name + ".json", jsonfolder)), outfilepath)

                imported = True
        except Exception as e:
            print(e)


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

    # cycling our JSON files
    for f in os.listdir(jsonfolder):
        write_sentences(clean_sentences(get_raw_sentences(
            f, jsonfolder)), outfilepath)


'''
    given sentences (all in one line), sanitizer and a mapping
    return a list of cleaned sentences
'''


def clean_sentences(raw_sentences):

    # custom sanitizer: this should replace all
    # carriages return with ''
    # otherwise sentences are broken while sanitizing
    raw_sentences = raw_sentences.replace("\n", " ")

    raw_sentences = sanitizer.prepare_splitlines(raw_sentences)
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
        [u'<i>', u''],
        [u'‒', u''],  # seems that this boy is a though one
        [u'&amp;amp;', u'&'],  # double strange ampersand probably an error
        [u'&amp;quot;', u''],
        [u'&amp;', u'&'],
        [u'&lt;br&gt;', u''],
        [u'&lt;', u''],
        [u'&gt;', u''],
        [u'<b><b><b><b><b><b><b><b><b><b>', u''],
        [re.compile("[A-Z]{2}:"), u''],  # remove speaker id
        # remove dots in thousands
        [re.compile("([0-9]+)\.([0-9]+)"), r"\1\2"],
        # remove quotes
        [re.compile(" '([^ ][^'^0-9]*[A-zàèìòùé]{2,}),{0,1}'"), u" \g<1> "],
        # words that ends in ita' probably are ità,
        [re.compile("([A-Za-z]{2,}it)a'"), u'\g<1>à'],
        [u"'nḥnw 'dyyn k'n", u''],  # a very custom one
        [re.compile("([A-Za-z]{2,})o'"), u'\g<1>ò'],  # pero' cio' lavorero'
        [u" sta' ", u' sta '],
        [u" da' ", u' dà '],
        [re.compile("([A-Za-z]+ch)e'"), u'\g<1>é'],
        [re.compile("([A-Za-z]{3,})a'([^A-Za-z]|$)"), u'\g<1>à '],  # words with a' -> à
        [re.compile("([A-Za-z]{3,})i'([^A-Za-z]|$)"), u'\g<1>ì '],  # words with i' -> ì
        [re.compile("[Qq]ui' "), u'qui '],
        [re.compile("([A-Za-z]{2,})u',{0,1} "), u'\g<1>ù '],
        [re.compile("([Cc]os)i'"), u'\g<1>ì'],
        [u" fu' ", u' fu '],
        [re.compile("([cC]')[eE]'"), u'\g<1>è'],
        [re.compile("É "), u'è '],
        [re.compile("XXesimo"), u'ventesimo'],
    ]
    ## WARNING: "Ašhadu ʾan lā ʾilāha ʾilla (A)llāh" . How handle this?
    raw_sentences = sanitizer.maybe_normalize(
        raw_sentences, mapping_normalization,mapping_append=False)
    sentences_list = []
    # list of sentences by using regex, because of special punctuation
    sentences = re.split(r'[."?!\n]\s*', raw_sentences)

    # other custom rules
    tobeverb = re.compile(" [e,E]'|^[e,E]'|'E'")
    tribu = re.compile("tribu'")
    piu = re.compile(" piu'")
    last_accent_fix = re.compile("([A-Za-z]{2,})([aeiou])(')( )([aeiou])")
    accentwithapostrophe = re.compile("([àÀèÈìÌòÒùÙéÉ])'")
    qual_e = re.compile("([Qq]ual)'e'")
    apo_tobe_verb = re.compile("([A-Za-z]+')(e')")
    plain2accent = {
        "a": u"à",
        "e": u"è",
        "i": u"ì",
        "o": u"ò",
        "u": u"ò",
    }
    for s in sentences:
        # check if sentence starts with "'"
        if(s is not None and len(s) >= 10):
            # sorry sentence I just hate you
            if u'´' in s:
                continue
            if u'`' in s:
                continue
            s = sanitizer.clean_single_line(s)
            s = piu.sub("più", s)
            s = tobeverb.sub(" è", s)
            s = tribu.sub("tribù", s)
            # last fix (maybe) for ' in place of of accents
            res = last_accent_fix.findall(s)
            for el in res:
                s = re.sub(r"".join(el), ''.join(
                    [el[0], plain2accent.get(el[1].lower()), el[3], el[4]]), s)
            s = accentwithapostrophe.sub(u'\g<1>', s)
            s = qual_e.sub(u'\g<1> è', s)
            s = apo_tobe_verb.sub(u'\g<1>è',s)
            s = re.sub("[Ee]ta'", "età", s)
            s = re.sub("[Gg]ia'", "già", s)
            s = re.sub("[Cc]ioe'", "cioè", s)
            s = re.sub("[Pp]uo'", "può", s)
            s = re.sub(r"( |^)[Ll]a'( |$|,)", u" là ", s)  # la' -> là
            s = re.sub(r"( |^)[Ll]i'( |$|,)", u" lì ", s)  # li' -> lì
            s = s.replace("IXX", u"") # invalid roman number
            s = re.sub("[sS]ta'", "sta", s)
            s = re.sub("[Ne]e'", "né", s)
            s = re.sub("([sS]ettiman[ae]|[Aa]nn[io]|[tT]emp[io]) ([fF]a)'",u'\g<1> fa', s) #  fa without '
            s = re.sub(" [A-Za-z]{0,}([lL]{1,}'$|[Uu]n'$)","",s) # sentences that ends with un' or ll'
            s = re.sub(" '([^'][A-Za-z0-9 ,.;]{0,})'$",u" \g<1>", s) # unquote some quotes
            s = re.sub("([SsDd])i'", u'\g<1>'.lower()+u'ì', s)
            # "[bBcCdDfFgGhHiIjJkKlLmMnNpPqQrRsStTuUvVwWxXyYzZ]'$| '$"
            sentences_list.append(s)

    return sentences_list


'''
    given a json, return a group of sentences
'''


def get_raw_sentences(json_file_name, jsonfolder):
    raw_sentences = ""

    # loading json data
    filehl = open(jsonfolder + os.path.sep + json_file_name, 'rb')
    filedata = filehl.read()
    json_data = (json.loads(filedata))

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
    outfile_hl.close()

if os.environ.get("TED_DEBUG") is not None:
    print("Parsing local JSONs")
    parse_all_json()
else:
    main()
