#!/usr/bin/env python3

import time
import os
import re
from corpora_importer import ArchiveImporter,Corpus,encoding_from_path
from glob import glob
CORPUS_NAME = 'm-ailabs'

class MAILabsImporter(ArchiveImporter):


    def get_corpus(self):
        SKIP_LIST = [] ## filter(None, CLI_ARGS.skiplist.split(","))
        ##extract training and development datasets
        ##do data merge, ArchiveImporter make final train/test/dev datasets
        utterances = {}
        audios = []

        wav_root_dir = os.path.join(self.origin_data_path,'it_IT')

        # Get audiofile path and transcript for each sentence in tsv
        samples = []
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
                    audio = os.path.join(os.path.dirname(record), "wavs", re[0] + ".wav")
                    transcript = re[2]
                    samples.append((audio, transcript))            
                    ##append data manifest
                    utterances[audio] = transcript
                    audios.append(audio)

        ##collect corpus
        corpus = Corpus(utterances,audios)
        #################
        ## evalita2009 have clips WAV 16000Hz - 1 chnl
        ## not require resample
        corpus.make_wav_resample = False
        return corpus

if __name__ == "__main__":

    corpus_name=CORPUS_NAME
    archivie_url = 'https://www.caito.de/data/Training/stt_tts/it_IT.tgz'

    data_dir = None
    ##data_dir = 'F:\\DATASET-MODELS\\speech_dataset\\CORPORA-IT-AUDIO\\M-AILABS'
    m_ailabs_importer = MAILabsImporter(corpus_name,archivie_url,data_dir=data_dir)
    
    m_ailabs_importer.run()