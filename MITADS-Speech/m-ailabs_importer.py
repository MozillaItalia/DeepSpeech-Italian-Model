#!/usr/bin/env python3

import time
import os
import re
from corpora_importer import ArchiveImporter,Corpus,encoding_from_path
from glob import glob
import numpy
CORPUS_NAME = 'm-ailabs'


##in MLS normalization of character '’'  is  wrong in transcription normalization (https://github.com/MozillaItalia/DeepSpeech-Italian-Model/issues/124)
def fix_apostrophe(text_source, text_normalized,fixed_token):
    
    if('’' in text_source):

        tokens = text_source.split()
        for tok in tokens:
            if('’' in tok):
                wrong_token = tok.replace('’','')
                right_token = tok.replace('’','\'')
                text_normalized = text_normalized.replace(wrong_token,right_token)

                fixed_token[wrong_token] = right_token

    return text_normalized


class MAILabsImporter(ArchiveImporter):


    ##see MLS importer and  this: https://github.com/MozillaItalia/DeepSpeech-Italian-Model/issues/124
    def save_wrong_token_dictionary(self,fixed_token):
        
        ###save wrong token to fix for reuse in MLS importing. Here we have the same problem but dont have raw data of wrong text
        with open( os.path.join(self.dataset_output_path,'mailabs_fixed_token.txt') , 'w',encoding='utf-8') as out:
            for key, value in fixed_token.items():
                out.write(key + ' ' + value + '\n')
                    

    def get_corpus(self):
        SKIP_LIST = [] ## filter(None, CLI_ARGS.skiplist.split(","))
        ##extract training and development datasets
        ##do data merge, ArchiveImporter make final train/test/dev datasets
        utterances = {}
        audios = []

        fixed_token = {}
        wav_root_dir = os.path.join(self.origin_data_path,'it_IT')

        bad_examples = self.get_bad_examples()

        # Get audiofile path and transcript for each sentence in tsv
        glob_dir = os.path.join(wav_root_dir, "**/metadata.csv")
        for record in glob(glob_dir, recursive=True):
            if any(
                map(lambda sk: sk in record, SKIP_LIST)
            ):
                continue

            enc = encoding_from_path(record)
            with open(record, "r",encoding=enc) as rec:
                for re in rec.readlines():
                    re = re.strip().split("|")

                    filename = re[0]
                    ##filter bad examples (https://github.com/MozillaItalia/DeepSpeech-Italian-Model/issues/124#issuecomment-798613031)
                    if(filename in bad_examples):
                        continue
                    audio = os.path.join(os.path.dirname(record), "wavs", filename + ".wav")
                    transcript_source = re[1]
                    transcript = re[2]
                    ##in MLS normalization of character '’'  is  wrong in transcription normalization
                    transcript =  fix_apostrophe(transcript_source,transcript,fixed_token)    

                    ##append data manifest
                    utterances[audio] = transcript  
                    audios.append(audio)

        ##collect corpus
        corpus = Corpus(utterances,audios)
        #################
        ## evalita2009 have clips WAV 16000Hz - 1 chnl
        ## not require resample
        corpus.make_wav_resample = True

        ##self.save_wrong_token_dictionary(fixed_token)


        return corpus

    def validate_label(self,label):

        # For now we can only handle [a-z ']
        if re.search(r"[0-9]|[(<\[\]&*{]", label) is not None:
            return None

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
        label = label.replace("’", "'") 
        label = label.replace("î", "i") 
        label = label.replace("ó", "o") 

        label = label.strip()
        label = label.lower()


        return label if label else None

    def get_speaker_id(self,audio_file_path):

        #filename =os.path.basename(audio_file_path)
        if('lisa_caputo' in audio_file_path):
            return 'lisa_caputo'
        elif('riccardo_fasol' in audio_file_path):
            return 'riccardo_fasol' 
        else:
            ##is mixed speaker ,... but 'novelle' group by speaker so we can generate a speaker_id
            filename =os.path.basename(audio_file_path)
            speaker_id = ''
            if('novelle_per_un_anno_00' in audio_file_path):
                speaker_id = 'mailabs-mix-0-0'
            elif('novelle_per_un_anno_13' in audio_file_path): 
                t = filename.split('_')
                speaker_id = 'mailabs-mix-'+ t[5] + '_' + t[7]
            else:                
                t = filename.split('_')
                speaker_id = 'mailabs-mix-'+ t[0].replace('novelle','') + '_' + t[1]
            return speaker_id

    def get_bad_examples(self):

        black_list = []
        ##transcription does not match with spoken words :
        ##audio is truncated before the end of transcription

        black_list.append("novelle06_16_pirandello_f000028")
        black_list.append("novelle06_16_pirandello_f000029")
        black_list.append("novelle06_16_pirandello_f000030")
        black_list.append("novelle06_16_pirandello_f000031")
        black_list.append("novelle06_16_pirandello_f000032")
        black_list.append("novelle06_16_pirandello_f000033")
        black_list.append("novelle06_16_pirandello_f000034")
        black_list.append("novelle06_16_pirandello_f000035")
        black_list.append("novelle06_16_pirandello_f000036")
        black_list.append("novelle06_16_pirandello_f000037")
        black_list.append("novelle06_16_pirandello_f000038")
        black_list.append("novelle06_16_pirandello_f000039")
        black_list.append("novelle06_16_pirandello_f000040")
        black_list.append("novelle06_16_pirandello_f000041")

        black_list.append("novelle06_17_pirandello_f000387")

        return black_list

if __name__ == "__main__":

    from corpora_importer import importer_parser
    args = importer_parser.parse_args()

    corpus_name=CORPUS_NAME
    archivie_url = 'https://www.caito.de/data/Training/stt_tts/it_IT.tgz'

    m_ailabs_importer = MAILabsImporter(corpus_name,archivie_url,data_dir=args.download_directory,output_path=args.csv_output_folder)
    
    m_ailabs_importer.run()