
#!/usr/bin/env python3

#from typing import List, Set, Dict, Tuple, Optional
import requests
import time
import os
from os import path, makedirs 
import ntpath
import random
import re
import logging
import progressbar 
from zipfile import ZipFile
import tarfile
from multiprocessing import Pool
import subprocess
from utils.downloader import SIMPLE_BAR, maybe_download
from collections import Counter
logging.basicConfig(level=logging.DEBUG)
import sox
from charset_normalizer import CharsetNormalizerMatches as CnM

from ds_ctcdecoder import Alphabet  
import csv
import argparse

SAMPLE_RATE = 16000
BITDEPTH = 16
N_CHANNELS = 1
MAX_SECS = 60 ##20
MIN_SECS = 0 # 1 ##zero second audio (probably) means one-word speech

AUDIO_EXTENSIONS = [".wav", ".mp3"]
AUDIO_WAV_EXTENSIONS = [".wav"]
AUDIO_MP3_EXTENSIONS = [".mp3"]

##DeepSpeech training code require all csv start whith columns "wav_filename", "wav_filesize", "transcript"
FIELDNAMES_CSV_MINIMAL = ["wav_filename", "wav_filesize", "transcript","speaker_id"]
FIELDNAMES_CSV_FULL = ["wav_filename", "wav_filesize", "transcript","speaker_id","duration","comments","source_transcript"]
BASE_OUTPUT_FOLDER_NAME = 'MITADS-Speech-output'

DEBUG_ALPHABET = ' ,\',a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z,à,è,é,ì,í,ò,ó,ô,ù,ú'.split(',')

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest="subcommand")
subparsers.required = True
importer_parser = subparsers.add_parser('importer')
importer_parser.add_argument('-d', '--download_directory', type=str, default=None,
                          help='Folder root where corpus downloaded'
                               'default is root project folder')

importer_parser.add_argument('-o', '--csv_output_folder', type=str, default=None,
                          help='where save csv'
                               'default is root project folder')



def is_audio_file(filepath):
    return any(
        os.path.basename(filepath).lower().endswith(extension) for extension in AUDIO_EXTENSIONS
    )

def is_audio_mp3_file(filepath):
    return any(
        os.path.basename(filepath).lower().endswith(extension) for extension in AUDIO_MP3_EXTENSIONS
    )

def is_audio_wav_file(filepath):
    return any(
        os.path.basename(filepath).lower().endswith(extension) for extension in AUDIO_WAV_EXTENSIONS
    )


def string_escape(s,encoding_from ="latin1", encoding='utf-8'):

    try:        
        return (s.encode(encoding_from)         # To bytes, required by 'unicode-escape'
                .decode('unicode-escape') # Perform the actual octal-escaping decode
                .encode(encoding_from)         # 1:1 mapping back to bytes
                .decode(encoding))        # Decode original encoding
    except:
        return (s.encode('utf-8')  ## cp1252     
                .decode('unicode-escape') 
                .encode('utf-8')  
                .decode(encoding))   

def get_counter():
    return Counter({'all': 0, 'failed': 0, 'invalid_label': 0, 'too_short': 0, 'too_long': 0, 'imported_time': 0, 'total_time': 0})


def encoding_from_path(txt_file_path):
    file_encoding ='utf-8'                   
    enc = CnM.from_path(txt_file_path).best().first()
    file_encoding = enc.encoding
    ##fix same encoding 
    if(file_encoding=='big5' or file_encoding=='cp1252' ):
        file_encoding = 'utf-8'  
    return file_encoding   

class Corpus:
    def __init__(self,utterences:dict,audios:list,datasets_sizes = [0.8,0.1,0.1],make_wav_resample=False): 

        ##utterences:dict --> key: audio_file_full_path  value:utterance 
        ## audios is a list of all audio_file , full absolute path
        ## datasets_sizes: dimension of train-test-dev datasets (in different csv)
        self.utterences = utterences
        self.audios = audios
        self.datasets_sizes = datasets_sizes
        self.make_wav_resample = make_wav_resample



class ArchiveImporter:
    def __init__(self,corpus_name,archive_url,extract_dir=None,output_path=None, data_dir=None,csv_append_mode=False,filter_alphabet=None):
        self.corpus_name=corpus_name
        self.archive_url=archive_url
        # Make archive_name from archive_filename
        self.archive_filename = self.archive_url.rsplit('/', 1)[-1]
        # os.path.splitext:
        # tar.gz: will split ("file.name.tar",".gz")
        # but will split correctly "cnz_1.0.0.zip" into ("cnz_1.0.0","zip")
        self.archive_name = os.path.splitext(self.archive_filename)[0]
        if self.archive_name.endswith(".tar"):
          self.archive_name = self.archive_name.replace(".tar","")
        self.extract_dir = self.archive_name
        if extract_dir is not None:
            self.extract_dir = extract_dir        
        # Making path absolute root data or prefered from param data_dir
        self.dataset_path = os.path.abspath(self.corpus_name) if data_dir==None else  os.path.join(data_dir, self.corpus_name)
        
        self.origin_data_path = os.path.join(self.dataset_path, "origin") if data_dir==None else  data_dir

        if (output_path==None):
            #default
            importers_output_dir = os.path.abspath(BASE_OUTPUT_FOLDER_NAME)
            if not path.exists(importers_output_dir):
                print('No path "%s" - creating ...' % importers_output_dir)
                makedirs(importers_output_dir)

            self.dataset_output_path = os.path.join(importers_output_dir,self.corpus_name)  
        else:
            ##exernal dir
            self.dataset_output_path = os.path.join(output_path, self.corpus_name) 

        self.csv_append_mode = csv_append_mode
        self.filter_max_secs = MAX_SECS ##filter for single clips max duration in second
        self.filter_min_secs = MIN_SECS ##filter for single clips min duration in second

        if(data_dir!=None):
            self.csv_wav_absolute_path = True
        else:
            ##default
            ##relative path from importers_output
            self.csv_wav_absolute_path = False

        ########################        
        self.ALPHABET = Alphabet(filter_alphabet) if filter_alphabet!=None else None
        ##SKIP_LIST = filter(None, CLI_ARGS.skiplist.split(","))
        ##validate_label = get_validate_label(CLI_ARGS)

    def run(self):
        self._download_and_preprocess_data()

    # Validate and normalize transcriptions. Returns a cleaned version of the label
    # or None if it's invalid.
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
        label = label.replace("î", "i") ##on mailabs dataset
        ##
        label = label.strip()
        label = label.lower()

        ##DEBUG - decomment for checking normalization char by char
        #for c in label:
        #    if(c not in DEBUG_ALPHABET):
        #        print('CHECK char:'+ c)

        return label if label else None


    # Validate and normalize transcriptions. Returns a cleaned version of the label
    # or None if it's invalid.
    def __validate_label(self,label):

      
        ## single apex
        #label = label.replace("’", "'") ##on siwis dataset
        ##label = label.replace("-", " ") ##on siwis dataset
        #label = label.replace("ï", "i") ##on siwis dataset

        ##
        label = label.strip()
        label = label.lower()

        ##TEMP - deccoment for check normalization to do
        for c in label:
            if(c not in DEBUG_ALPHABET):
                print('CHECK char:'+ label)
                break

        return label if label else None


    def preprocess_trascript(self,transcript):


        #if CLI_ARGS.normalize:
        #    label = (
        #        unicodedata.normalize("NFKD", label.strip())
        #        .encode("ascii", "ignore")
        #        .decode("ascii", "ignore")
        #    )

        transcript = self.validate_label(transcript)
        if self.ALPHABET and transcript and not self.ALPHABET.CanEncode(transcript):
            print('Alphabet not encode: {} '.format(transcript))
            transcript = None

        return transcript


    def _download_and_preprocess_data(self):

        if not path.exists(self.dataset_output_path):
            print('No path "%s" - creating ...' % self.dataset_output_path)
            makedirs(self.dataset_output_path)

        archive_filename = self.archive_url.rsplit('/', 1)[-1]
        # Conditionally download data
        extracted_path = os.path.join(self.origin_data_path, self.extract_dir)
        if not os.path.exists(extracted_path):
            archive_path = maybe_download(archive_filename, self.origin_data_path, self.archive_url)
            # Conditionally extract common voice data
            self._maybe_extract(self.origin_data_path,self.extract_dir, archive_path)
       
        ##get corpus:  audio_file_names + transcriptions
        print('Filter audio file and parse transcript...')
        corpus = self.get_corpus()

         # Conditionally convert CSV files and mp3/wav data to DeepSpeech CSVs and wav
        self._maybe_convert_sets(corpus)      

    def _maybe_extract(self,target_dir, extract_dir, archive_path):
        # If target_dir/extract_dir does not exist, extract archive in target_dir
        extracted_path = os.path.join(target_dir, extract_dir)
        if not os.path.exists(extracted_path):
            print(f"No directory {extracted_path} - extracting archive...")

            ##check file if zip or tar
            if(archive_path.endswith('.zip')):
                ##extraxt zip file
                with ZipFile(archive_path, "r") as zipobj:
                    # Extract all the contents of zip file in current directory
                    zipobj.extractall(target_dir)
            else:
                ##extract other gzip, bz2 and lzma
                tar = tarfile.open(archive_path)
                tar.extractall(target_dir)
                tar.close()
        else:
            print(f"Found directory {extracted_path} - not extracting it from archive.")


    ##override this to use full functionality
    def get_corpus(self) -> Corpus :    
        print('must be implemented in importer')

    ## OPTIONAL: must be implemented in importer if exist speaker id information
    def get_speaker_id(self,audio_file_path):
        return ""

    def _maybe_convert_sets(self,corpus:Corpus):

        samples = corpus.audios
        num_samples = len(samples)
        if(num_samples==0):
            return

        ## all examples are processed, even if the resample is not necessary, the duration or other filters should be evaluated
        samples = [ [a,corpus.make_wav_resample, corpus.utterences[a]] for a in corpus.audios ] 
        ##self.one_sample(samples[0])
        # Mutable counters for the concurrent embedded routine
        counter = get_counter()
        print(f"Converting audio files to wav {SAMPLE_RATE}hz Mono")
        pool = Pool()
        bar = progressbar.ProgressBar(max_value=num_samples, widgets=SIMPLE_BAR)
        rows = []
        for i, processed in enumerate(pool.imap_unordered(self.one_sample,samples), start=1):
            counter += processed[0]
            rows += processed[1]
            bar.update(i)
        bar.update(num_samples)
        pool.close()
        pool.join()        
       
        ########################################
        ## filtered rows data are evaluated in write_csv
        self._write_csv(corpus,rows)

    def _maybe_convert_wav(self,orig_filename, wav_filename):
        ## MP2/MP3 (with optional libmad, libtwolame and libmp3lame libraries)  ## http://sox.sourceforge.net/Docs/Features
        if not os.path.exists(wav_filename):
            transformer = sox.Transformer()
            transformer.convert(samplerate=SAMPLE_RATE,n_channels=N_CHANNELS, bitdepth=BITDEPTH)
            try:
                transformer.build(str(orig_filename), str(wav_filename))
            except (sox.core.SoxError,sox.core.SoxiError) as ex:
                print("SoX processing error", ex, orig_filename, wav_filename)

    ##overrider this to filter
    def row_validation(self,filename,duration,comments):
        ##return True 
        return True

    def one_sample(self,sample):

        orig_filename = sample[0]
        make_wav_resample = sample[1]
        original_trascription = sample[2]

        head_f, f = ntpath.split(orig_filename)

        ##if is wav files we keep the original to carry out the import several times (for regeneration csv files)
        if(make_wav_resample and is_audio_wav_file(orig_filename)) :                
            converted_folder = os.path.join(os.path.dirname(orig_filename),'converted')
            if not os.path.exists(converted_folder):
                ##catch multiprocessor makedirs error
                try:
                    makedirs(converted_folder)
                except:
                    pass

            wav_filename = os.path.join(converted_folder,f)
        else:
            # Storing wav files next to the audio filename ones - just with a different suffix
            wav_filename = path.splitext(orig_filename)[0] + ".wav"

        ##Note: to get frames/duration for mp3/wav audio we not use soxi command but sox.file_info.duration(
        ##soxi command is not present in Windows sox distribution  - see this  https://github.com/rabitt/pysox/pull/74
        
        duration = -1
        try:
            duration = sox.file_info.duration(orig_filename)
        except:
            ## some mp3 in lablita got in error
            print('sox.file_info.duration error on file {}, retrieve duration via filesize'.format(orig_filename))
            pass               
        
        comments = ""
        try:
          comments=sox.file_info.comments(orig_filename)
        except (UnicodeError,sox.SoxiError) as e:
          try:
            completedProcess=subprocess.run(["soxi", "-a", orig_filename], stdout=subprocess.PIPE)
            comments=completedProcess.stdout.decode("utf-8", "ignore")
          except:
            pass

        if(len(comments)>0):
            comments = comments.replace('\r', '')## 
            comments = comments.replace('\n', '|')## \n is csv line separator


        if(make_wav_resample):
            self._maybe_convert_wav(orig_filename, wav_filename)            
  
        file_size = -1
        if os.path.exists(wav_filename):
            file_size = path.getsize(wav_filename)
            if(duration==-1):
                ##retrieve duration from file size
                ##duration = (file_size - 44) / 16000 / 2
                ## time = FileLength / (Sample Rate * Channels * Bits per sample /8)
                duration = file_size /(SAMPLE_RATE * N_CHANNELS * BITDEPTH/8 )

        frames = duration * SAMPLE_RATE

        is_valid = self.row_validation(orig_filename,duration,comments)

        label =  self.preprocess_trascript(original_trascription)  ##label not managed  ##validate_label(sample[1])
        
        speaker_id = ''
        ##get speaker id info
        if(label!=None):
            ##            
            try:
                speaker_id = self.get_speaker_id(orig_filename)
            except Exception as e:
                print('get_speaker_id error: ' + str(e)) 
        
        rows = []
        counter = get_counter()
        if file_size == -1:
            # Excluding samples that failed upon conversion
            print(f'Conversion failed {orig_filename}')
            counter["failed"] += 1
        elif label is None or label=='' or not is_valid:
            # Excluding samples that failed on label validation
            print('Exclude label '+original_trascription)
            counter["invalid_label"] += 1
        elif False and int(frames / SAMPLE_RATE * 1000 / 10 / 2) < len(str(label)):
            # Excluding samples that are too short to fit the transcript
            counter["too_short"] += 1
        elif frames / SAMPLE_RATE > self.filter_max_secs:
            # Excluding very long samples to keep a reasonable batch-size
            print(f' Clips too long, {str(frames / SAMPLE_RATE)}  - {orig_filename}')

            counter["too_long"] += 1
        else:
            # This one is good - keep it for the target CSV
            rows.append((wav_filename, file_size, label,speaker_id,duration,comments,original_trascription))
            counter["imported_time"] += frames
        counter["all"] += 1
        counter["total_time"] += frames
        return (counter, rows)


    def one_sample_librosa(self,sample):

        import librosa

        mp3_wav_filename = sample[0]
        make_wav_resample = sample[1]
        # Storing wav files next to the audio filename ones - just with a different suffix
        wav_filename = path.splitext(mp3_wav_filename)[0] + ".wav"
        
        duration = -1
        comments = ""
        audioData, frameRate = None,None
        try:
            ##load data and convert to mono
            ## Warning -  libsndfile does not (yet/currently) support the mp3 format. see  https://github.com/librosa/librosa/issues/1015
            ## TODO: Installing ffmpeg to FIX error audioread.exceptions.NoBackendError - Lablita mp3 - problem is a missing ogg vorbis codec for audioread -  see also : https://github.com/librosa/librosa/issues/219
            audioData, frameRate = librosa.load(mp3_wav_filename, sr=SAMPLE_RATE, mono=True)   
            duration = librosa.get_duration(y=audioData, sr=SAMPLE_RATE)          
        except Exception as e: 
            raise(e)
            print(str(e))           
            print('error load audio data with Librosa lib, retrieve duration via filesize - {}'.format(mp3_wav_filename))
            pass  


        if(make_wav_resample and audioData!=None):
            ## Maybe convert wav whith Librosa
            if not os.path.exists(wav_filename):            
                ##load audio
                ##y, sr = librosa.load(mp3_filename, sr=SAMPLE_RATE)

                ##resample stereo to mono
                #y_mono = librosa.to_mono(y)                
                ##librosa.resample(y,sr,)
                librosa.output.write_wav(wav_filename, audioData, SAMPLE_RATE)         
  
        file_size = -1
        if os.path.exists(wav_filename):
            file_size = path.getsize(wav_filename)
            if(duration==-1):
                ##retrieve duration from file size
                ##duration = (file_size - 44) / 16000 / 2
                ## time = FileLength / (Sample Rate * Channels * Bits per sample /8)
                duration = file_size /(SAMPLE_RATE * N_CHANNELS * BITDEPTH/8 )

        frames = duration * SAMPLE_RATE

        is_valid = self.row_validation(mp3_wav_filename,duration,comments)

        label = '' ##label not managed  ##validate_label(sample[1])
        rows = []
        counter = get_counter()
        if file_size == -1:
            # Excluding samples that failed upon conversion
            print(f'Conversion failed {mp3_wav_filename}')
            counter["failed"] += 1
        elif label is None or not is_valid:
            # Excluding samples that failed on label validation
            counter["invalid_label"] += 1
        elif int(frames / SAMPLE_RATE * 1000 / 10 / 2) < len(str(label)):
            # Excluding samples that are too short to fit the transcript
            counter["too_short"] += 1
        elif frames / SAMPLE_RATE > self.filter_max_secs:
            # Excluding very long samples to keep a reasonable batch-size
            print(f' Clips too long, {str(frames / SAMPLE_RATE)}  - {mp3_wav_filename}')

            counter["too_long"] += 1
        else:
            # This one is good - keep it for the target CSV
            rows.append((mp3_wav_filename, file_size, label,duration,comments))
            counter["imported_time"] += frames
        counter["all"] += 1
        counter["total_time"] += frames
        return (counter, rows)

    def ___one_sample(sample):
        if is_audio_file(sample):
            y, sr = librosa.load(sample, sr=16000)

            # Trim the beginning and ending silence
            yt, index = librosa.effects.trim(y)  # pylint: disable=unused-variable

            duration = librosa.get_duration(yt, sr)
            if duration > MAX_SECS or duration < MIN_SECS:
                os.remove(sample)
            else:
                librosa.output.write_wav(sample, yt, sr)
    

    def _write_csv(self,corpus:Corpus,filtered_rows):

        print("\n")
        print("Writing CSV files")
        audios = corpus.audios
        utterences = corpus.utterences
        csv_data = []

        csv_columns = FIELDNAMES_CSV_FULL

        samples_len = len(audios)
        for row_data in filtered_rows:
            
            wav_filename = row_data[0]
            file_size = row_data[1]
            transcript_processed = row_data[2]
            speaker_id = row_data[3]
            duration = row_data[4]
            comments = row_data[5]            
            source_transcript = row_data[6]          
            
            wav_file_path = None
            if(self.csv_wav_absolute_path):
                ## audio file 
                #   audio files and  output csv are on different paths
                ##audio file absolute path
                wav_file_path = os.path.abspath(wav_filename)
            else:                 
                ##make relative path audio file
                wav_file_path =  os.path.relpath(wav_filename, self.origin_data_path)                
   
            csv_row =  dict(
                            wav_filename=wav_file_path,
                            wav_filesize=file_size,
                            transcript=transcript_processed,
                            speaker_id=speaker_id,
                            duration=duration,
                            comments=comments,
                            source_transcript = source_transcript ##we save original transcript
                        )
            csv_data.append(csv_row)

        #shuffle set
        random.seed(76528)
        random.shuffle(csv_data)

        train_len = int(samples_len*corpus.datasets_sizes[0])
        test_len = int(samples_len*corpus.datasets_sizes[1])
        if(samples_len<train_len+test_len):
            raise('size of the test dataset must be less than {}'.format(str(samples_len-train_len)))

        dev_len = samples_len - train_len - test_len
        train_data = csv_data[:train_len]
        dev_data = csv_data[train_len:train_len+test_len]
        test_data = csv_data[train_len+test_len:]

        file_open_mode = 'a' if self.csv_append_mode else 'w'

        target_csv_template = os.path.join(self.dataset_output_path, "{}.csv") 
        with open(target_csv_template.format("train_full"), file_open_mode, encoding="utf-8", newline="") as train_full_csv_file:  
            with open(target_csv_template.format("train"), file_open_mode, encoding="utf-8", newline="") as train_csv_file:  
                with open(target_csv_template.format("dev"), file_open_mode, encoding="utf-8", newline="") as dev_csv_file:  
                    with open(target_csv_template.format("test"), file_open_mode, encoding="utf-8", newline="") as test_csv_file:  
                        
                        train_full_writer = csv.DictWriter(train_full_csv_file, dialect='excel-tab', fieldnames=FIELDNAMES_CSV_FULL)
                        if not self.csv_append_mode:
                            train_full_writer.writeheader()
                        train_writer = csv.DictWriter(train_csv_file, dialect='excel-tab', fieldnames=FIELDNAMES_CSV_FULL)
                        if not self.csv_append_mode:
                            train_writer.writeheader()
                        dev_writer = csv.DictWriter(dev_csv_file, dialect='excel-tab', fieldnames=FIELDNAMES_CSV_FULL)
                        if not self.csv_append_mode:
                            dev_writer.writeheader()
                        test_writer = csv.DictWriter(test_csv_file, dialect='excel-tab', fieldnames=FIELDNAMES_CSV_FULL)
                        if not self.csv_append_mode:
                            test_writer.writeheader()
                        
                        ##train full
                        for row in csv_data:
                            train_full_writer.writerow(row)
                        ##train
                        for row in train_data:
                            train_writer.writerow(row)
                        ##dev
                        for row in dev_data:
                            dev_writer.writerow(row)
                        ##test
                        for row in test_data:
                            test_writer.writerow(row)

        print(f"Wrote {len(csv_data)} entries")


    

#if __name__ == "__main__":

 
