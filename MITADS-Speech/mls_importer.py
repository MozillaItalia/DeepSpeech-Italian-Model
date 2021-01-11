
#!/usr/bin/env python3

import time
import os
import re
from corpora_importer import ArchiveImporter,Corpus

CORPUS_NAME = 'mls'

class MLSImporter(ArchiveImporter):


    def get_corpus(self): 
        ##extract training and development datasets
        ##do data merge, ArchiveImporter make final train/test/dev datasets
        utterances = {}
        audios = []        
        count=0
        for d in ("train","dev","test"): 
            #
            #if(count==1):
            #    break           
            wav_dir = os.path.join(self.origin_data_path, self.archive_name, d , "audio")
            transcript_path = os.path.join(self.origin_data_path, self.archive_name, d, "transcripts.txt")
            
            with open(transcript_path) as fin:
                for line in fin:  
                    t_s = re.split(r'\t+', line)   
                    
                    flac_file_path_t = t_s[0].split('_')
                    file_name =  t_s[0] + ".flac"
                    audio_file_path =  os.path.join( wav_dir,flac_file_path_t[0],flac_file_path_t[1],file_name)
                    transcript = t_s[1].strip()                         
                    ##append data manifest
                    utterances[audio_file_path] = transcript
                    audios.append(audio_file_path)
                    count +=1

                    #if(count==1):
                    #    break

        ##collect corpus
        corpus = Corpus(utterances,audios)
        #################
        ##  
        ##  audio .flac require resample
        corpus.make_wav_resample = True
        return corpus

if __name__ == "__main__":

    corpus_name=CORPUS_NAME
    archivie_url = 'https://dl.fbaipublicfiles.com/mls/mls_italian.tar.gz'
    data_dir = None
    data_dir = "F:\\DATASET-MODELS\\speech_dataset\\CORPORA-IT-AUDIO\\MLS-LM"
    output_dir = None
    output_dir = "F:\\DATASET-MODELS\\speech_dataset\\new-speech-corpora-it"

    mls_importer = MLSImporter(corpus_name,archivie_url,data_dir=data_dir,output_path=output_dir)
    
    mls_importer._download_and_preprocess_data()