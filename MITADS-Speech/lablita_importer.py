#!/usr/bin/env python3


from bs4 import BeautifulSoup
import requests
import time
import os
import urllib
import csv
import logging
from corpora_importer import ArchiveImporter
logging.basicConfig(level=logging.DEBUG)


ANNOTATION_DICT = ['0','1','2','3','4','5','6','7','8','9','-','+','[',']','<','>']
ANNOTATION_PAUSE = '/'
##incomprehensible word
ANNOTATION_WORD_INC = 'xxx'


def main(output_root_dir):

    corpus_name = 'lablita'
    base_importer = ArchiveImporter(corpus_name,'')
    ##filter max 1 minute, then corpora_collector apply final filter on duration
    base_importer.filter_max_secs = 60

    filter_italian_enabled=True
    # to calculate time elapsed later
    start_time = time.time()

    # create output folder
    output_ipic_folder =  os.path.join(output_root_dir, corpus_name)
    
    if not os.path.exists(output_ipic_folder):
        os.mkdir(output_ipic_folder)

    # sub folders
    corpus_output_folder = os.path.join(output_ipic_folder, 'audios')
    if not os.path.exists(corpus_output_folder):
        os.mkdir(corpus_output_folder)   

    # write unique csv for all transcription
    outfilepath = os.path.join(output_ipic_folder, 'train_full.csv')

    csv_file = open(outfilepath,"w+",encoding="utf8")
    fh_out = csv.writer(csv_file,quoting=csv.QUOTE_NONNUMERIC)
    
    ##fh_out.writerow(['filename','filesize','transcript','transcript_annotated'])
    fh_out.writerow(['speaker_id','wav_filename','wav_filesize','transcript','duration','comments'])
 

    #to improve performance we write on the append file for the whole download, but comparisons test needed
    #csv_file.close()

    ############################
    baseurl = "http://www.lablita.it/app/dbipic/"
    #######################################
    search_endpoint1 = "search.php?from=index"  ## 20844 hits - 1043 pages

    ##choose second link,must large,  but it includes entries in other languages
    search_endpoint2 = "search2.php"  # 38464 hits -  1924 pages (20' for page)
    #################################################
    headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
            'Content-Type' :'multipart/form-data'}

    pagenumber = 1
    the_end = False
    logging.debug('Start DB-IPIC Import Data from url {}'.format(baseurl))
    
    count_audio_imported = 0
    while(not the_end):
 
        
        ## perform request 
        ## curl test
        #curl --verbose --request POST --header "Content-Type:multipart/form-data" --form "pag=3"  http://www.lablita.it/app/dbipic/search2.php
        ##NOTE1: to perform requests.post with multipart-data we need to pass both files and data argument with same content 
        ##NOTE2: whit headers=headers in post argument i have a problem to retrieve rigth page number
        files = {'pag': pagenumber}
        req = requests.post(baseurl + search_endpoint2 ,  files=files, data = {'pag' :pagenumber},timeout=60) ##headers=headers,

        data = req.text  
        logging.debug('Process Page {}'.format(str(pagenumber)))
        soup = BeautifulSoup(data, 'html.parser')  # BeautifulSoup html extraction

        ##section clip start with div className file
        div_files = soup.findAll("div", {"class": "file"})       

        the_end = True
        if(div_files!=None):

            ##clip information is in sequential html elements
            ##so we scroll through the div==files to parse the individual blocks
            for div_file in div_files:

                parsed_filename = ''
                parsed_speaker_name = ''
                parsed_term_sequence = ''
                parsed_text_unit_tag = []
                parsed_text_unit_text = []
                parsed_audio_link = ''
                curr_parsing = ''
     
                parsed_text_curr_unit = []
                count_elem=0
                for elem in div_file.next_elements:

                    if(count_elem==0):
                        parsed_filename = elem.next
                        count_elem +=1
                        continue

                    count_elem +=1
                    if(isinstance(elem,str) and elem=='\n'):
                        continue

                    if(not isinstance(elem,str)):
                        elem_class_name = elem['class'][0] if elem.has_attr('class') else ''

                        if(elem_class_name=='turn'):
                            curr_parsing = 'turn'
                        elif(elem_class_name=='termseq'):
                            curr_parsing = 'termseq'                            
                        elif(elem_class_name=='tu_table_cell'):
                            curr_parsing = 'tu_table_cell'  
                        elif(elem_class_name=='txt_row'):
                            curr_parsing = 'txt_row'  
                        elif(elem_class_name=='dlaudio'):
                            curr_parsing = 'dlaudio'  
                            ##get href link mp3
                            parsed_audio_link = baseurl + elem['href']
                            break
                    else:
                        if(curr_parsing=='turn'):
                            parsed_speaker_name = elem
                        elif(curr_parsing=='termseq'):
                            parsed_term_sequence = elem                         
                        elif(curr_parsing=='tu_table_cell'):
                            ##text-unit
                            parsed_text_unit_tag.append(elem)
                            parsed_text_curr_unit = []
                            ##append trascription of a single text-unit
                            parsed_text_unit_text.append(parsed_text_curr_unit)
                        elif(curr_parsing=='txt_row'):
                            parsed_text_curr_unit.append(elem)
                        elif(curr_parsing=='dlaudio'):                            
                            ##already taken
                            break
                
                if(len(parsed_text_unit_text)>0 and parsed_filename!=''):

                    ##filter italian clips 
                    ##  filename start whit first char of current language code (example ifamcv01, epubmn03, bfamdl05)
                    if(filter_italian_enabled and parsed_filename[:1]!='i'):
                        ##continue other page for sure to take all clips 
                        the_end = False
                        continue

                    ##collect all text unit parsed
                    transcript_annotaded = ''.join([''.join(unit) for unit in parsed_text_unit_text])

                    ##filter incomprehensible sentences
                    if(ANNOTATION_WORD_INC in transcript_annotaded):
                        continue                    

                    ## clear annotation
                    text_cleaned = clear_transcript(transcript_annotaded)

                    ##build filename
                    parsed_filename_full = parsed_filename + '_' + parsed_term_sequence

                    ## save mp3
                    down_file = save_audio(parsed_filename_full,parsed_audio_link,corpus_output_folder)
                    
                    ##resample mp3 to wav 
                    preprocessed = base_importer.one_sample([down_file,True])
                    rows = preprocessed[1]

                    if(len(rows)==0):
                        ##skip, mp3 filtered or not resampled
                        continue
                    ##########################

                    logging.debug('Import audio+text, file {}'.format(parsed_filename_full))

                    ##export flat version of text whit all annotation
                    text_annotaded = parse_text_annotation(parsed_text_unit_tag,parsed_text_unit_text) 
                    text_annotaded = parsed_speaker_name + ":"+text_annotaded
                    ####                         
                    row = [parsed_filename_full,0,text_cleaned,text_annotaded]
                    fh_out.writerow(row)
                    
                    ##################################################################
                    ##continue paging until you find items 
                    the_end = False
                    pass
                else:
                    print('ERROR VALIDATION _ FIX CODE !!!')
                    raise('error parsing page!')
                
        else:
            ##nessun risultato
            the_end = True
            pass

        pagenumber += 1

    csv_file.close()    
    print('####################FINISH!###########################################################')
    print("Time elapsed: " + str(int(int(time.time() - start_time) / 60)) + " minutes")



def clear_transcript( transcript_annotaded,remove_pause_ann=True):
    trans_clean_ann = [c for c in transcript_annotaded if c not in ANNOTATION_DICT]
    if(remove_pause_ann):
        trans_clean_ann = [c for c in trans_clean_ann if c!=ANNOTATION_PAUSE]
    trans_clean_ann = ''.join(trans_clean_ann)

    return trans_clean_ann


def parse_text_annotation(parsed_text_unit_tag,parsed_text_unit_text):

    text_annotaded = '' 
    for i in range(len(parsed_text_unit_tag)):
        text_unit = parsed_text_unit_tag[i]
        transcript_ann_unit = ''.join(parsed_text_unit_text[i]) 
        text_annotaded += transcript_ann_unit + '(' + text_unit + ')'
    return text_annotaded


def parse_text_annotation2(parsed_text_unit_tag,parsed_text_unit_text):

    text_annotaded = ''
    text_ann_1 = ''    
    for i in range(len(parsed_text_unit_tag)):
        text_unit = parsed_text_unit_tag[i]
        transcript_ann_unit = ''.join(parsed_text_unit_text[i]) 
        text_annotaded += transcript_ann_unit + '(' + text_unit + ')'
        text_ann_1 += transcript_ann_unit

    text_whit_only_pause = clear_transcript(text_ann_1,remove_pause_ann=False)
    return text_annotaded,text_whit_only_pause


def save_audio(filename,audio_path,output_dir):
    #file_txt = output_dir + filename + '.txt'
    #with open(file_txt, 'w') as filetowrite:
    #    filetowrite.write(transcription)

    file_mp3 = output_dir + filename + '.mp3'
    urllib.request.urlretrieve (audio_path, file_mp3)
    
    ##resample wave
    return file_mp3


if __name__ == "__main__":

    output_root_dir = os.path.dirname(os.path.abspath(__file__))

    if len(sys.argv) > 1:
        output_root_dir = sys.argv[1]

    main(output_root_dir)