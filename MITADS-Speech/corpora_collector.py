
#!/usr/bin/env python3

import time
import os
import re
from os import path, makedirs 
import ntpath
from pathlib import Path
import random
import logging
import progressbar 
from utils.downloader import SIMPLE_BAR

from multiprocessing import Pool
from shutil import copyfile 
import yaml ## pip install PyYAML
from corpora_importer import BASE_OUTPUT_FOLDER_NAME,FIELDNAMES_CSV_MINIMAL,FIELDNAMES_CSV_FULL
import csv
import zipfile
import argparse
from random import randrange
random.seed(10)

logging.basicConfig(level=logging.DEBUG)

FIELDNAMES_CSV = ["wav_filename", "wav_filesize", "transcript","speaker_id","duration"] 


parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest="subcommand")
subparsers.required = True
collector_parser = subparsers.add_parser('collector')
collector_parser.add_argument('-c', '--config_file', type=str, default=os.path.join(os.path.dirname(__file__),'assets','corpora_collector', 'mitads-speech-v0.1.yaml'),
                          help='Configuration of current collector'
                               'Default is assets/mitads-speech-v0.1.yaml')

collector_parser.add_argument('-o', '--csv_folder', type=str, default=os.path.abspath(BASE_OUTPUT_FOLDER_NAME),
                          help='root folder of csv dataset to collect, also is root of output csv'
                               'default is root_project/MITADS-Speech-output')

collector_parser.add_argument('-d', '--dataset_output', type=str, default='',
                          help='root folder output dataset'
                               'default is csv_folder')

collector_parser.add_argument('-z', '--zip_output', type=str, default='true',
                          help='if true collect files into .zip. If false files are copyed to a folder in csv_folder')



def load_corpora_config(config_file_path):
    config = None
    with open(config_file_path, 'r') as stream:        
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            raise(exc)
    return config
    

def get_wav_filename_abs_path(csv_wav_filename,csv_corpus_rootdir,corpus_name):
    if(not os.path.isabs(csv_wav_filename)):
        ##is relative path
        file_name = csv_wav_filename.rsplit('/', 1)[-1]
        wav_filename_path = os.path.join(csv_corpus_rootdir,corpus_name,'audios',file_name)
    else:
        return csv_wav_filename

def execute_dataset_balancing(corpus_rows,save_vocab=True):
    ##ESEGUI BILANCIAMENTO
    from utils.collector_util import create_vocabulary,get_min_corpus_cover_vocab,save_vocabulary
    vocab = create_vocabulary(corpus_rows)
    if(save_vocab):
        save_vocabulary(vocab,os.path.join(corpora_output_dir,'vocab.txt')) 

    corpus_rows = get_min_corpus_cover_vocab(corpus_rows,vocab)

    return corpus_rows

def speaker_filter(csv_rows,min_speaker_minute):

    speakers_rows = {}
    speakers_duration = {}
    ret_rows = []
    for row in  csv_rows:        
        speaker_id = row[3]
        duration =float(row[4])
        if(speaker_id==None or speaker_id==''):
            ##unknown speaker
            continue

        dur = speakers_duration.get(speaker_id,0)
        dur +=duration
        curr_rows = speakers_rows.get(speaker_id,[])
        curr_rows.append(row)
        speakers_duration[speaker_id] = dur
        speakers_rows[speaker_id] = curr_rows

    ##check min minute filter
    for speaker_id, duration in speakers_duration.items(): 
        if(duration>= min_speaker_minute*60):
            ##ok
            ret_rows.extend(speakers_rows[speaker_id])

    return ret_rows
        


def get_info_and_stats(csv_rows):
    ##############
    ##get info and stats
    total_duration = 0
    ##total_size = 
    speakers_data = {}
    corpus_stats = {}
    min_audio_duration = 9999
    max_audio_duration = 0
    ####################
    unknown_speaker_corpus = {}

    ##check unique filename and replace path 
    for row in  csv_rows:
        
        speaker_id = row[3]
        duration =float(row[4])      
    
        corpus_name = row[7]
  
        ######################
        ##append info report

        curr_corpus_stats = corpus_stats.get(corpus_name,{})
        corpus_stats[corpus_name] = curr_corpus_stats

        total_duration +=duration

        min_audio_duration = duration if duration<min_audio_duration else min_audio_duration
        max_audio_duration = duration if duration>max_audio_duration else max_audio_duration

        curr_speaker_data = None
        if(speaker_id not in speakers_data):
            curr_speaker_data = {'corpus':corpus_name,'minutes':0}
            speakers_data[speaker_id]  = curr_speaker_data
        else:
            curr_speaker_data = speakers_data[speaker_id]
        curr_speaker_data['minutes'] = curr_speaker_data['minutes'] + duration/60

        if(speaker_id==''):
            #unknow speaker
            unknown_speaker_corpus[corpus_name] = True
        #################
        c_duration = curr_corpus_stats.get('duration',0)
        spekaers_curr = curr_corpus_stats.get('speakers',set())
        spekaers_curr.add(speaker_id)
        c_duration += duration
        curr_corpus_stats['duration'] = c_duration
        curr_corpus_stats['speakers'] = spekaers_curr
        ###########################

    global_stats = {'total_duration':total_duration,'min_audio_duration':min_audio_duration,'max_audio_duration':max_audio_duration}
    
    return (corpus_stats,speakers_data,unknown_speaker_corpus,global_stats)


def collect_datasets(config,args):
    


    zip_output = True if args.zip_output.lower()=='true' else False
    csv_corpus_rootdir = args.csv_folder

    final_dataset_root = csv_corpus_rootdir if args.dataset_output=='' else  args.dataset_output
    
    corpus2collect = config['corpus2collect']


    ######append 
    #corpus2collect = ['mls'] ## 'evalita2009','siwis','mspka'
    ##if wav location is in onother device, fill this list
    #corpus2collect_alt_dir = {}

    #corpora_output_dir = os.path.abspath('collected_corpora')

    split_final_dataset = config.get('split_final_dataset',"0")
    split_final_dataset = int(split_final_dataset) if int(split_final_dataset)>=2 else None
    
    csv_rel_path_linux = config.get('csv_rel_path_linux', True)


    final_corpora_name = config['name']
    final_corpora_version = config['version']
    output_corpora_foldername = final_corpora_name + '_' + 'v' + final_corpora_version
    corpora_output_dir = os.path.join(final_dataset_root, output_corpora_foldername)

    if not path.exists(corpora_output_dir):
        print('No path "%s" - creating ...' % corpora_output_dir)
        makedirs(corpora_output_dir)

    
    csv_rows = []


    count_filename_renamed = 0

    for corpus_name  in corpus2collect:     
        
        ##filter sample based on configuration file  - ex. duration , comments        
        curr_corpus_csv_path = os.path.join(csv_corpus_rootdir,corpus_name,'train_full.csv')
        if(not os.path.exists(curr_corpus_csv_path)):
            raise ValueError('file not found: {}'.format(curr_corpus_csv_path))

        print("Filter and Collect Corpus {}...".format(curr_corpus_csv_path))

        corpus_rows = filter_corpus(curr_corpus_csv_path,config['corpus2collect'][corpus_name])
        
        ########################################
        
        ##check unique filename and replace path 
        for row in  corpus_rows:
            wav_filename_path = row[0]

            
            ##check if file exist
            wav_filename_path = get_wav_filename_abs_path(wav_filename_path,csv_corpus_rootdir,corpus_name)
            if(not os.path.exists(wav_filename_path)):
                raise ValueError('file {} not exist'.format(wav_filename_path))

            ###override path with absolute
            row[0] = wav_filename_path
            ################
            row.append(corpus_name) ##need for stats report
            # temporarily append the final absolute path of wav, it will be removed when collect wav files            
            #row.append(wav_destination_path)

            ##append row
            csv_rows.append(row)
            ######################            

    ############
    ##balance
    if(config.get('vocabulary_balance',False)==True):
        print("vocabulary_balance...")
        csv_rows = execute_dataset_balancing(csv_rows)
    
    if(config.get('min_speaker_minute',None)!=None):
        print("Filter Speakers...")
        csv_rows = speaker_filter(csv_rows,config['min_speaker_minute'])
    
    ##################################
    #random.seed(76528)
    random.shuffle(csv_rows) 

    ##get stats
    corpus_stats,speakers_data,unknown_speaker_corpus,global_stats = get_info_and_stats(csv_rows)
    ##
 
    ########################
    all_filenames = []

    dataset_parts = []
    if(split_final_dataset==None):
        ##generate one final dataset folder
        dataset_parts.append((None,csv_rows))
    else:
        ##generate final dataset slitted
        len_sub = int(len(csv_rows)/split_final_dataset)
        for i in range(split_final_dataset):
            #scurr_len =  len(csv_rows) - len_sub*(split_final_dataset-1) if i==split_final_dataset-1 else len_sub
            
            if(i<split_final_dataset-1):                
                dataset_parts.append((output_corpora_foldername + '_sub{}'.format(i),csv_rows[len_sub*i:len_sub*(i+1)]))
            else:
                dataset_parts.append((output_corpora_foldername + '_sub{}'.format(i),csv_rows[len_sub*i:len(csv_rows)]))

    list_4_copy = []
    count = 0
    for data in dataset_parts:
        count +=1
        #if(count==2):
        #    break

        sub_folder = data[0]
        _csv_rows = data[1]

        corpora_wav_output_dir = None
        _corpora_output_dir = None
        if(sub_folder==None):
            _corpora_output_dir = corpora_output_dir
        else:
            _corpora_output_dir = os.path.join(corpora_output_dir,sub_folder)
            if not path.exists(_corpora_output_dir):
                print('No path "%s" - creating ...' % _corpora_output_dir)
                makedirs(_corpora_output_dir)  

        corpora_wav_output_dir = os.path.join(_corpora_output_dir,'audios')

        if not path.exists(corpora_wav_output_dir):
            print('No path "%s" - creating ...' % corpora_wav_output_dir)
            makedirs(corpora_wav_output_dir)   
        ##

        final_csv_rows = []    
        for row in _csv_rows:
            wav_filename_path = row[0]
            corpus_name = row[7]

            ########################################  
            head, tail = ntpath.split(wav_filename_path)
            wav_filename = tail
            if(wav_filename in all_filenames):
                ## in foxfroge, wav files with the same name belong to different speakers who pronounce the same utterance
                ##rename file name destination: 
                wav_filename = wav_filename[0:len(wav_filename)-4] + '-copy-'+ str(count_filename_renamed) + '.wav'
                count_filename_renamed+=1
                #if(wav_filename in all_filenames):
                #    raise ValueError('duplicate filename audio {}, not managed yet!'.format(wav_filename))

            all_filenames.append(wav_filename)

            ## filename destination (copyed) - create subfolder with corpora name - 
            wav_destination_root = os.path.join(corpora_wav_output_dir,corpus_name)
            if not path.exists(wav_destination_root):
                print('No path "%s" - creating ...' % wav_destination_root)
                makedirs(wav_destination_root)
            wav_destination_path = os.path.join(wav_destination_root,wav_filename)
            ##########################################
            ##append path- need when copy file 
            row.append(wav_destination_path)
            ##########################################
                
            ##for csv row must be dict
            new_row={}     
            #wav_destination_path = row[-1]   ##destination - sposta qui gestione  
            ##wav relative path
            wav_file_final_rel_path = os.path.relpath(wav_destination_path,_corpora_output_dir)

            if(csv_rel_path_linux):
                ## it only takes effect if the dataset is generated on windows
                wav_file_final_rel_path = wav_file_final_rel_path.replace('\\','/')

            new_row[FIELDNAMES_CSV[0]] = wav_file_final_rel_path
            transcription , speaker_id,duration =row[2], row[3],row[4]
            duration = float(duration)
            new_row[FIELDNAMES_CSV[1]] = row[1]
            new_row[FIELDNAMES_CSV[2]] = transcription
            new_row[FIELDNAMES_CSV[3]] = speaker_id 
            new_row[FIELDNAMES_CSV[4]] = duration

            final_csv_rows.append(new_row)

        list_4_copy.extend(_csv_rows)

        ####write final csv - 
        write_csv(final_csv_rows,_corpora_output_dir)
        ####################################


    ##write report file
    ##TODO pass map for all parameter
    write_report(corpora_output_dir,corpus_stats,speakers_data,unknown_speaker_corpus,global_stats)

    #############################

    ##zip folder output
    if(zip_output):
        ## NOT TESTED
        ## ZIP WITH COMMAND LINE _ 7Zip
        ##copy collected files to file archive (.zip)
        global ziph

        archive_file_path = corpora_output_dir + '.zip'
        print("Zipping Corpora...") 

        ziph = zipfile.ZipFile(archive_file_path, 'w', zipfile.ZIP_DEFLATED)
        ##copy csv
        ziph.write(os.path.join(corpora_output_dir, "train.csv"),'train.csv')
        ziph.write(os.path.join(corpora_output_dir, "dev.csv"),'dev.csv')
        ziph.write(os.path.join(corpora_output_dir, "test.csv"),'test.csv')
        ziph.write(os.path.join(corpora_output_dir, "train_full.csv"),'train_full.csv')

        ziph.write(os.path.join(corpora_output_dir, "metainfo.txt"),'metainfo.txt')

        pool = Pool()
        bar = progressbar.ProgressBar(max_value=len(list_4_copy), widgets=SIMPLE_BAR)
        for i, _ in enumerate(pool.imap_unordered(zip_one, list_4_copy), start=1):
            bar.update(i)

        bar.update(len(list_4_copy))
        pool.close()
        pool.join()

        ziph.close()
        #zip_corpora(corpora_output_dir)
        print("Successfull Generated Corpora {}".format(archive_file_path))
        ### delete source folder
    else:
        ##copy collected files to folder
        print("Copy Wav files to {}")
        pool = Pool()
        bar = progressbar.ProgressBar(max_value=len(list_4_copy), widgets=SIMPLE_BAR)
        for i, _ in enumerate(pool.imap_unordered(_maybe_copy_one, list_4_copy), start=1):
            bar.update(i)

        bar.update(len(list_4_copy))
        pool.close()
        pool.join()
    ###########################################


def zip_one(row):
    global ziph

    original_wav_path = row[0]
    _, curr_filename = ntpath.split(original_wav_path)
    ziph.write(original_wav_path,os.path.join('audios',curr_filename))


def write_report(corpora_output_dir,corpus_stats,speakers_data,unknown_speaker_corpus,global_stats):
    
   
    total_duration = global_stats['total_duration']
    min_audio_duration = global_stats['min_audio_duration']
    max_audio_duration = global_stats['max_audio_duration']
    with open(os.path.join(corpora_output_dir,'metainfo.txt'),'w') as file:
        h = (total_duration/60)/60


        file.write('\n')
        file.write('\n')
        file.write('MITADS - Mozilla Italia Deep Speech\n')
        file.write('Italian Speech Dataset\n')
        file.write('\n')
        file.write('{}\n'.format(config['name']))
        file.write('Version {} \n'.format(config['version']))
        file.write('\n')
        file.write('###################################################\n')
        file.write('\n')
        
        file.write('COLLECTED COPRUS      MINUTES      SPEAKERS\n')
        file.write('\n')
        for corpus_name, curr_corpus_stats in corpus_stats.items():
            #curr_corpus_stats = corpus_stats[corpus_name]
            duration = curr_corpus_stats.get('duration',0)
            spekaers_curr = curr_corpus_stats.get('speakers',set())
            file.write('{}{}{}\n'.format(corpus_name.ljust(22), str(round((duration/60),2) ).ljust(13),str(len(spekaers_curr))  ))
        
        file.write('\n')
        file.write('\n')
        file.write('\n')
        file.write('###################################################\n')
        file.write('\n')
        file.write('Total Duration:         {} hours\n'.format(str(round(h,2) )))
        
        file.write('Max audio duration:     {}   second\n'.format(str(round(max_audio_duration,3) )))
        file.write('Min audio duration:     {} second\n'.format(str(round(min_audio_duration,4) )))
        file.write('\n')

        ##sub unknown speaker if present
        n_speakers = len(speakers_data)-1 if len(unknown_speaker_corpus)>0 else len(speakers_data)
        file.write('Number of Speakers: {}\n'.format(n_speakers))
        if len(unknown_speaker_corpus)>0:
            from itertools import chain
            middles_corpus = ','.join(unknown_speaker_corpus.keys())
            file.write('No speakers identified in corpus: {} \n'.format(middles_corpus))
        file.write('\n')
        file.write('###################################################\n')
        file.write('\n')
        file.write('\n')
        file.write('\n')
        file.write('SPEAKER                 CORPUS          MINUTES     \n')
        file.write('\n')
        for speakers_id, data in speakers_data.items():
             file.write('{}{}{}'.format(speakers_id.ljust(24),data['corpus'].ljust(16),str(round(data['minutes'],2) )))
             file.write('\n')

def write_csv(samples,output_path,train_size=0.8,test_size=0.1):


    samples_len = len(samples)
    train_len = int(samples_len*train_size)
    test_len = int(samples_len*test_size)
    if(samples_len<train_len+test_len):
        raise('size of the test dataset must be less than {}'.format(str(samples_len-train_len)))
    

    dev_len = samples_len - train_len - test_len
    train_data = samples[:train_len]
    dev_data = samples[train_len:train_len+test_len]
    test_data = samples[train_len+test_len:]
    
    #shuffle set train/dev/test

    ##
    ##train_full sorted by speaker_id
    from operator import itemgetter
    samples = sorted(samples, key=lambda k: k['speaker_id'])   
    ## sorted(l, key=lambda x: x[2])
    ## l.sort(key=lambda x: x[2]) ##inplace

    ##
    file_open_mode = 'w'
    csv_dialect = 'excel'  ## coma separated  - no excel-tab
    target_csv_template = os.path.join(output_path, "{}.csv") 
    with open(target_csv_template.format("train_full"), file_open_mode, encoding="utf-8", newline="") as train_full_csv_file:  
        with open(target_csv_template.format("train"), file_open_mode, encoding="utf-8", newline="") as train_csv_file:  
            with open(target_csv_template.format("dev"), file_open_mode, encoding="utf-8", newline="") as dev_csv_file:  
                with open(target_csv_template.format("test"), file_open_mode, encoding="utf-8", newline="") as test_csv_file:  
                    
                    train_full_writer = csv.DictWriter(train_full_csv_file, dialect=csv_dialect, fieldnames=FIELDNAMES_CSV)
                    train_full_writer.writeheader()
                    train_writer = csv.DictWriter(train_csv_file, dialect=csv_dialect, fieldnames=FIELDNAMES_CSV)
                    train_writer.writeheader()
                    dev_writer = csv.DictWriter(dev_csv_file, dialect=csv_dialect, fieldnames=FIELDNAMES_CSV)
                    dev_writer.writeheader()
                    test_writer = csv.DictWriter(test_csv_file, dialect=csv_dialect, fieldnames=FIELDNAMES_CSV)
                    test_writer.writeheader()
                    
                    ##train full
                    for row in samples:
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

    print(f"Wrote {len(samples)} entries")

def filter_row(row,max_duration_filter,comments_contains_filter):
    #wav_filepath = row[0]
    #filesize = row[1]
    trascript = row[2]
    #speaker_id = row[3]
    duration = float(row[4])
    comments = row[5]
    filtered = False
    ###filtering rows
    if(max_duration_filter!=None):
        if(duration>max_duration_filter):
            return True

    if(comments_contains_filter!=None and comments!=''):
        for text in comments_contains_filter:
            if(text in comments):
                return True

    return False

def filter_corpus(csv1_path,config):

    filter_cfg = config.get('filter',{}) if config !=None else {} 
    max_duration_filter = filter_cfg.get('max_duration',None)
    comments_contains_filter = filter_cfg.get('comments_contains',None)
    
    f = open(csv1_path,encoding='utf-8')
    next(f) # skip the header   

    output_rows = []
    for line in f:
        row = re.split('\t',line)
        ## for order see corpora_importer FIELDNAMES_CSV_FULL
        wav_filepath = row[0]
        filesize = row[1]
        trascript = row[2]
        speaker_id = row[3]
        duration = -1
        try:
            duration = float(row[4])
        except Exception as e:
            raise(e)
        comments = row[5]

        if(not filter_row(row,max_duration_filter,comments_contains_filter)):
            ##add
            output_rows.append(row) ##append only column : wav_filename + filesize + transcript + speaker_id
        else:
            ##filtered
            pass 

    f.close() # not really needed
    return output_rows

def _maybe_copy_one(sample):

    original_wav_path = sample[0]
    destination_wav_path = sample[-1] ##last column we append destination path

    if(os.path.isfile(destination_wav_path)):
        ##file exist , skip
        return

    ##copy file
    copyfile(original_wav_path, destination_wav_path)

 
if __name__ == "__main__":


    args = collector_parser.parse_args()

    config = load_corpora_config(args.config_file)

    collect_datasets(config,args)