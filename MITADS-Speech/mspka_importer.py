#!/usr/bin/env python3
import time
import os
import re
from corpora_importer import ArchiveImporter,Corpus

CORPUS_NAME = 'mspka'
SILENCE_ANNOTATION ='sil'

class MSPKAImporter(ArchiveImporter):


    def get_corpus(self):
        ##extract training and development datasets
        ##do data merge, ArchiveImporter make final train/test/dev datasets
        utterances = {}
        audios = []
        wav_dir  = os.path.join(self.origin_data_path, self.archive_name, "wav_1.0.0")
        text_dir = os.path.join(self.origin_data_path, self.archive_name, "lab_1.0.0")
        

        ##iterate wav file current folder
        for fname in os.listdir(wav_dir):

            fname = os.fsdecode(fname)
            if(not fname.lower().endswith('.wav')):
                continue

            wav_file_path = os.path.join(wav_dir, fname)
            txt_file_path = os.path.join(text_dir, fname.split('.')[0]+'.lab')
            if(not os.path.isfile(txt_file_path)):
                print('audio file {} doesn\'t have a file transcript'.format(str(wav_file_path)))
                continue

            ##read file transcript
            transcript = ''
            transcript_annotaded = ''
            with open(txt_file_path) as f:
                transcript_annotaded = f.readlines()

            ##parse annotation - build a clean transcript   
            transcript_toks = []
            for line in transcript_annotaded:  

                row_data = line.split()
                if(len(row_data)<=3):
                    ##no transcrit here
                    continue

                annotation = row_data[2]
                if(annotation==SILENCE_ANNOTATION):
                    continue
                curr_text = row_data[3:] 
                curr_text = ' '.join(curr_text)
                ##clear text -   accented char escape
                curr_text = string_escape(curr_text)
                transcript_toks.append(curr_text)

            transcript = ' '.join(transcript_toks)
            transcript = transcript.strip()
            ##append data manifest
            utterances[wav_file_path] = transcript
            audios.append(wav_file_path)  

        ##collect corpus
        corpus = Corpus(utterances,audios)
        #################
        ## MSPKA need wav resample - clips is 22050Hz  353 kb/s (1 chnl)  
        ## 
        corpus.make_wav_resample = True
        return corpus

if __name__ == "__main__":

    corpus_name=CORPUS_NAME
    archivie_urls = []
    archivie_urls.append('http://www.mspkacorpus.it/MSPKA_data/session1/cnz_1.0.0.zip')
    archivie_urls.append('http://www.mspkacorpus.it/MSPKA_data/session1/lls_1.0.0.zip')
    archivie_urls.append('http://www.mspkacorpus.it/MSPKA_data/session1/olm_1.0.0.zip')
    
    for i in range(len(archivie_urls)):
        archivie_url = archivie_urls[i]
        csv_append_mode = not i==0
        mspka_importer = MSPKAImporter(corpus_name,archivie_url, csv_append_mode=csv_append_mode)
        
        mspka_importer.run()