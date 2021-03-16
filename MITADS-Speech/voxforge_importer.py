#!/usr/bin/env python3
import time
import os
import re
from corpora_importer import ArchiveImporter,Corpus,string_escape


import urllib
from bs4 import BeautifulSoup
import time
CORPUS_NAME = 'voxforge'

class VoxforgeImporter(ArchiveImporter):


    def get_corpus(self):
        ##extract training and development datasets
        ##do data merge, ArchiveImporter make final train/test/dev datasets
        utterances = {}
        audios = []
        wav_dir  = os.path.join(self.origin_data_path, self.archive_name, "wav")
        text_file = os.path.join(self.origin_data_path, self.archive_name, "etc","PROMPTS")  

        wav_files = [f for f in os.listdir(wav_dir) if os.path.isfile(os.path.join(wav_dir, f))]
        count=0

        with open(text_file,encoding='utf-8') as f:
            for line in f:
                temp_2 = line.split(" ", 1)
                ref_url = temp_2[0]
                transcript = temp_2[1].lower()
                transcript = transcript.replace('\n','')

                temp = ref_url.split('/')
                speaker_id = temp[0]
                file_n = temp[-1]
                for wav_file in wav_files:
                    if(file_n in wav_file):
                        ##found , is this
                        wav_file_path = os.path.join(wav_dir,wav_file)
                        utterances[ wav_file_path] = transcript
                        audios.append(wav_file_path) 
                        count +=1
                        break


        ##collect corpus
        corpus = Corpus(utterances,audios)
        #################
        ## VoxForge need wav resample
        ## 
        corpus.make_wav_resample = True
        return corpus

    def get_speaker_id(self,audio_file_path):

        return self.archive_name


def get_voxforge_bad_speaker():

    l = []
    l.append("anonymous-20080504-qvg")
    l.append("anonymous-20080723-ouv")
    l.append("anonymous-20080725-dey")
    l.append("Vistaus-20080718-mrm")
    #l.append("")
    #l.append("")


    return l



if __name__ == "__main__":

    from corpora_importer import importer_parser
    args = importer_parser.parse_args()

    corpus_name=CORPUS_NAME
    archivie_urls = []

    #voxforge_url = "http://www.repository.voxforge1.org/downloads/SpeechCorpus/Trunk/Audio/Main/16kHz_16bit"
    voxforge_url = "http://www.repository.voxforge1.org/downloads/it/Trunk/Audio/Main/16kHz_16bit/"


    html_page = urllib.request.urlopen(voxforge_url)
    soup = BeautifulSoup(html_page, "html.parser")

    # list all links
    archivies = [l["href"] for l in soup.find_all("a") if ".tgz" in l["href"]]

    bad_speakers = get_voxforge_bad_speaker()
    for i in range(len(archivies)):
        archivie_url = voxforge_url + '' + archivies[i]

        speaker_id = archivies[i].split('.')[0]

        if(speaker_id in bad_speakers):
            ##filter bad speaker
            print("filter speaker {}".format(speaker_id))
            continue

        csv_append_mode = not i==0

        _importer = VoxforgeImporter(corpus_name,archivie_url,data_dir=args.download_directory,output_path=args.csv_output_folder,csv_append_mode=csv_append_mode)
        
        try:
            _importer.run()
        except Exception as e:
            print(str(e))
            print('ARCHIVE CORRUPTED {}'.format(_importer.archive_name))
            ##some archive is corrupted, pass
            continue

        ##sleep ...host interrupt connection
        time.sleep(2)