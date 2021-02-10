
#!/usr/bin/env python3

import time
import os
import re
from corpora_importer import ArchiveImporter,Corpus

CORPUS_NAME = 'mls'

#function fix_apostrophe and load_mailabs_fixed_token
##see this: https://github.com/MozillaItalia/DeepSpeech-Italian-Model/issues/124
def fix_apostrophe(text_normalized,fixed_token):
    
    tokens = text_normalized.split()
    for tok in tokens:

        if(tok in fixed_token):
            ##replace works only if there are no ambiguous tokens like : destro ->d'estro  sera->s'era
            text_normalized = text_normalized.replace(tok,fixed_token[tok])

    return text_normalized


def load_mailabs_fixed_token():

    fixed_tokens = None

    ##mailabs_output_path = self.dataset_output_path
    #ft_filepath = os.path.join('assets','mailabs_fixed_token.txt')
    ##load file with ambigous token annotated with '<SKIP>'
    ft_filepath = os.path.join('assets','mailabs_fixed_token_no_ambig.txt')
    if(os.path.exists(ft_filepath)):
        fixed_tokens = {}

        with open( os.path.join(ft_filepath ,encoding='utf-8'))  as fin:
            for line in fin:
                t = line.split()
                wrong_tok = t[0]
                right_tok = t[1]
                fixed_tokens[wrong_tok] = right_tok

    return fixed_tokens



class MLSImporter(ArchiveImporter):


    def get_corpus(self): 

        ###open wrong token saved on M-AILABS importer  to fix apostrophe issue   
        #fixed_tokens = load_mailabs_fixed_token()

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
            
            with open(transcript_path,encoding="utf-8") as fin:
                for line in fin:  
                    t_s = re.split(r'\t+', line)   
                    
                    flac_file_path_t = t_s[0].split('_')
                    file_name =  t_s[0] + ".flac"
                    audio_file_path =  os.path.join( wav_dir,flac_file_path_t[0],flac_file_path_t[1],file_name)
                    transcript = t_s[1].strip()  
                    ###  fix apostrophe bug with raw data in m-ailabs - see https://github.com/MozillaItalia/DeepSpeech-Italian-Model/issues/124 
                    #transcript =  fix_apostrophe(transcript,fixed_tokens)               
                    ##append data manifest
                    utterances[audio_file_path] = transcript
                    audios.append(audio_file_path)
                    count +=1

                    #if(count==1):
                    #   break

        ##collect corpus
        corpus = Corpus(utterances,audios)
        #################
        ##  
        ##  audio .flac require resample
        corpus.make_wav_resample = True
        return corpus


    def get_speaker_id(self,audio_file_path):

        filename =os.path.basename(audio_file_path)
        speaker_id = filename.split('_')[0]
        # unique for other importer
        speaker_id = 'mls_'+speaker_id
        return speaker_id

    # Validate and normalize transcriptions. Returns a cleaned version of the label
    # or None if it's invalid.
    def validate_label(self,label):
      
        ## single apex
        ##label = label.replace("’", "'") ##on siwis dataset
        ##this char is in MLS transcript
        label = label.replace("-", " ") ##on siwis dataset
        label = label.replace("ï", "i") ##on siwis dataset
        ##
        label = label.strip()
        label = label.lower()
        ##TEMP - deccoment for check normalization to do
        #for c in label:
        #    if(c not in DEBUG_ALPHABET):
        #        print('CHECK char:'+ c)

        return label if label else None

    ##RENAME FUNCTION to row_validation to test filter by author in this importer. 
    ##As Alternative: since execution time for the import is long, this filtering operation ( subject to possible revisions) , could also be implemented in the next step in corpora_collector
    def ___row_validation(self,filename,duration,comments):
        is_valid = True
        if(comments==None or comments==''):
            return is_valid
        ##we dont parse string , only check if comment contains author
        filtered_author = ["Dante Alighieri", "Giovanni Francesco Straparola"]
        filtered = any(txt in comments for txt in filtered_author)
        is_valid = not filtered

        #if(not is_valid):
        #    print('filtered')
        #else:
        #    print(comments)

        return is_valid

if __name__ == "__main__":

    from corpora_importer import importer_parser
    args = importer_parser.parse_args()

    corpus_name=CORPUS_NAME
    archivie_url = 'https://dl.fbaipublicfiles.com/mls/mls_italian.tar.gz'

    mls_importer = MLSImporter(corpus_name,archivie_url, data_dir=args.download_directory,output_path=args.csv_output_folder)
    
    mls_importer.run()