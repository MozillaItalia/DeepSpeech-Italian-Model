#!/usr/bin/env python3

import time
import os
import re
from corpora_importer import ArchiveImporter,Corpus,string_escape

CORPUS_NAME = 'siwis'

class SiwisImporter(ArchiveImporter):


    def get_corpus(self):
        ##extract training and development datasets
        ##do data merge, ArchiveImporter make final train/test/dev datasets
        utterances = {}
        audios = []
        wav_dir  = os.path.join(self.origin_data_path, self.archive_name, "wav","IT")
        text_dir = os.path.join(self.origin_data_path, self.archive_name, "text","IT")
        
        for subdir, dirs, files in os.walk(wav_dir):
            uuu=0
            for _dir in dirs:
                curr_wav_dir =  os.path.join(subdir, _dir)
                curr_txt_dir =  os.path.join(text_dir, _dir)

                ##iterate wav file current folder
                for fname in os.listdir(curr_wav_dir):
                    fname = os.fsdecode(fname)

                    wav_file_path = os.path.join(wav_dir, _dir,fname)
                    txt_file_path = os.path.join(curr_txt_dir, fname.split('.')[0]+'.txt')
                    if(not os.path.isfile(txt_file_path)):
                        print('audio file {} doesn\'t have a file transcript')
                        continue

                    ##read file transcript
                    transcript = ''
                    with open(txt_file_path, "r") as f:
                        transcript += f.readline()
                    

                    transcript = transcript.strip()
                    transcript = string_escape(transcript)
                    ##append data manifest
                    utterances[wav_file_path] = transcript
                    audios.append(wav_file_path)     

        ##collect corpus
        corpus = Corpus(utterances,audios)
        #################
        ## SIWIS clips need resample wav - clips is 44100Hz  706 kb/s (1 chnl) 
        ## not require resample
        corpus.make_wav_resample = True
        return corpus


if __name__ == "__main__":

    corpus_name=CORPUS_NAME
    archivie_url = 'https://phonogenres.unige.ch/downloads/siwis_latest.zip'
    data_dir=None
    siwis_importer = SiwisImporter(corpus_name,archivie_url,  data_dir=data_dir)

    siwis_importer.run()