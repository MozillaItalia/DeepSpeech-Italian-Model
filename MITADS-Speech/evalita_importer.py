
#!/usr/bin/env python3

import time
import os
import re
from corpora_importer import ArchiveImporter,Corpus

CORPUS_NAME = 'evalita2009'
EVALITA_DICT_CONVERSION = { '0':'zero','1':'uno','2':'due','3':'tre','4':'quattro','5':'cinque','6':'sei','7':'sette','8':'otto','9':'nove'}

class EvalitaImporter(ArchiveImporter):


    def get_corpus(self):
        ##extract training and development datasets
        ##do data merge, ArchiveImporter make final train/test/dev datasets
        utterances = {}
        audios = []

        for d in ("development","training"):       
            wav_dir = os.path.join(self.origin_data_path, d)
            transcript_path = os.path.join(self.origin_data_path, self.archive_name, d+".txt")
            
            with open(transcript_path) as fin:
                for line in fin:                 
                    t_s = line.split(".wav", maxsplit=1)
                    audio_file_rel_path = t_s[0] + '.wav'
                    transcript = t_s[1].strip()

                    ###preprocess transcript - replace numbers from numeric to literal
                    transcript = ' '.join([EVALITA_DICT_CONVERSION.get(c,'') for c in transcript])
                    transcript =  re.sub(r'\s+', ' ', transcript)            
                    ## need absolute path for audios, separator cross os 
                    _audio_file_rel_path = ''.join([ os.path.sep if c=='/' else c for c in audio_file_rel_path])
                    audio_file_abs_path =  os.path.join(self.origin_data_path, _audio_file_rel_path )                
                    ##append data manifest
                    utterances[audio_file_abs_path] = transcript
                    audios.append(audio_file_abs_path)

        ##collect corpus
        corpus = Corpus(utterances,audios)
        #################
        ## evalita2009 have clips WAV 16000Hz - 1 chnl
        ## not require resample
        corpus.make_wav_resample = False
        return corpus

if __name__ == "__main__":

    corpus_name=CORPUS_NAME
    archivie_url = 'http://www.evalita.it/sites/evalita.fbk.eu/files/doc2009/evalita2009srt.zip'

    data_dir = None
    evalita_importer = EvalitaImporter(corpus_name,archivie_url,data_dir=data_dir)
    
    evalita_importer.run()