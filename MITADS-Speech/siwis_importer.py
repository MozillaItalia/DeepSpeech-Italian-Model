#!/usr/bin/env python3

import time
import os
import re
from corpora_importer import ArchiveImporter,Corpus,string_escape
from charset_normalizer import CharsetNormalizerMatches as CnM

CORPUS_NAME = 'siwis'

class SiwisImporter(ArchiveImporter):


    def get_corpus(self):
        ##extract training and development datasets
        ##do data merge, ArchiveImporter make final train/test/dev datasets
        utterances = {}
        audios = []
        wav_dir  = os.path.join(self.origin_data_path, self.extract_dir, "wav","IT")
        text_dir = os.path.join(self.origin_data_path, self.extract_dir, "txt","IT")
        ##read transcript in prompts.txt
        transcripts = {}
        ##encoding prompts files is cp1252
        encoding = 'cp1252'
        ###read transcript from prompts file
        with open(os.path.join(self.origin_data_path,self.extract_dir, "prompts","ALL_IT_prompts_iso.txt"), "r",encoding=encoding) as f:
            line = f.readline()
            while line:
                temp = re.split(r'\t', line)
                filename = temp[0]
                transcript = temp[1].strip()
                transcripts[filename] = transcript
                # use realine() to read next line
                line = f.readline()

        for subdir, dirs, files in os.walk(wav_dir):
            uuu=0
            for _dir in dirs:

                if(_dir=='converted'):
                    ##wav converted in a previous session run
                    continue

                curr_wav_dir =  os.path.join(subdir, _dir)
                #
                ##iterate wav file current folder
                for fname in os.listdir(curr_wav_dir):
                    fname = os.fsdecode(fname)
                    if(fname=='converted'):
                        ##skip wav converted by importer
                        continue
                    wav_file_path = os.path.join(wav_dir, _dir,fname) 

                    try:
                        transcript = transcripts[fname.replace('.wav','.txt')]
                    except:                        
                        curr_txt_dir =  os.path.join(text_dir, _dir)
                        txt_file_path = os.path.join(curr_txt_dir, fname.split('.')[0]+'.txt')
                        #print('missing prompts , read transcript from file {}'.format(txt_file_path))
                        if(not os.path.isfile(txt_file_path)):
                            raise ValueError('audio file {} doesn\'t have a file transcript'.format(wav_file_path))  
                            #continue
                        transcript = self.read_txt_file(txt_file_path) 
            
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

    def read_txt_file(self,txt_file_path):
        transcript = ''

        ##files have different encoding (utf-8, utf_16_be, etc..)
        ##need check to open file with correct encoding
        file_encoding ='utf-8'                   
        enc = CnM.from_path(txt_file_path).best().first()
        file_encoding = enc.encoding
        ##fix same encoding 
        if(file_encoding=='big5' or file_encoding=='cp1252' ):
            file_encoding = 'utf-8'                    

        with open(txt_file_path, "r",encoding=file_encoding) as f:
            transcript += f.readline()

        transcript = transcript.strip()
        return transcript

    def get_speaker_id(self,audio_file_path):
    
        _, _file = os.path.split(audio_file_path)
        temp = _file.split('_')
        speaker_id = temp[0] + '_' + temp[1] + '_' + temp[2] 

        return speaker_id

    # Validate and normalize transcriptions. Returns a cleaned version of the label
    # or None if it's invalid.
    def validate_label(self,label):
        ##import unicodedata
        ## normalize remove absent char è ò à
        #label = (
        #        unicodedata.normalize("NFKD", label.strip())
        #        .encode("ascii", "ignore")
        #        .decode("ascii", "ignore")
        #    )

        label = label.replace("-", " ")
        label = label.replace("_", " ")
        label = re.sub("[ ]{2,}", " ", label)
        label = label.replace(".", "")
        label = label.replace(",", "")
        label = label.replace(";", "")
        label = label.replace("?", "")
        label = label.replace("!", "")
        label = label.replace(":", "")
        label = label.replace("\"", "")
        ##        

        label = label.replace("’", "\'") 
        label = label.replace("´", "\'")  

        label = label.replace("»", "") 
        label = label.replace("«", "") 
        ############################
        label = label.replace("Ã", "a")##present , see 'domandÃ'
        ####
        
        label = label.replace("²", "") 
        label = label.replace("<", "")  
        label = label.replace(">", "") 
        label = label.replace("(", "") 
        label = label.replace(")", "") 

        label = label.replace("¿", "")
        label = label.replace("ｨ", "")
        label = label.replace("ﾃ", "")
        label = label.replace("兮", "")
        label = label.replace("窶", "") 
        

        ###number normalization
        label = label.replace("2002", "duemiladue")
        label = label.replace("'99", "novantanove")
        label = label.replace("'98", "novantotto")
        label = label.replace("'82", "ottantadue")
        label = label.replace("36", "trentasei")
        label = label.replace("20mila", "ventimila")

        label = label.replace("51", "cinquantuno")
        label = label.replace("21", "ventuno")
        label = label.replace("31%", "trentuno per cento")
        label = label.replace("16%", "sedici per cento")
        label = label.replace("2%", "due per cento")
        label = label.replace("741", "settecentoquarantuno")
        label = label.replace("103", "settecentoquarantuno")
        ######################## 
        ##other to clean
        label = label.replace("\ufeff", "")
        ##

        if re.search(r"[0-9]|[\[\]&*{]", label) is not None:
            return None

        label = label.strip()
        label = label.lower()

        ##DEBUG - decomment for checking normalization char by char
        #DEBUG_ALPHABET = ' ,\',a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z,à,è,é,ì,í,ò,ó,ô,ù,ú'.split(',')
        #for c in label:
        #    if(c not in DEBUG_ALPHABET):
        #        print('CHECK char:'+ c)

        return label if label else None

if __name__ == "__main__":

    from corpora_importer import importer_parser
    args = importer_parser.parse_args()
    #args.download_directory = "F:\\DATASET-MODELS\\speech_dataset\\CORPORA-IT-AUDIO\\SIWIS"
    #args.csv_output_folder = "F:\\DATASET-MODELS\\speech_dataset\\new-speech-corpora-it"

    corpus_name=CORPUS_NAME
    archive_url = 'https://phonogenres.unige.ch/downloads/siwis_latest.zip'

    siwis_importer = SiwisImporter(corpus_name,archive_url,extract_dir="siwis_database", data_dir=args.download_directory,output_path=args.csv_output_folder)

    siwis_importer.run()
