
#!/usr/bin/env python3

import time
import os
from os import path, makedirs 
import logging
import progressbar 
from utils.downloader import SIMPLE_BAR

from multiprocessing import Pool
from shutil import copyfile 

logging.basicConfig(level=logging.DEBUG)



corpus2collect = []
######append 
corpus2collect = ['evalita2009','siwis','mspka']
##if wav location is in onother device, fill this list
corpus2collect_alt_dir = {}

corpora_output_dir = os.path.abspath('collected_corpora')
corpora_wav_output_dir = os.path.join(corpora_output_dir,'audios')

fout_train = None
fout_test = None
fout_dev = None
fout_full_train = None
all_filenames= set()

def collect_datasets():
    

    if not path.exists(corpora_output_dir):
        print('No path "%s" - creating ...' % corpora_output_dir)
        makedirs(corpora_output_dir)
    if not path.exists(corpora_wav_output_dir):
        print('No path "%s" - creating ...' % corpora_wav_output_dir)
        makedirs(corpora_wav_output_dir)


    fout_train =open(os.path.join(corpora_output_dir,'train.csv',),"a",encoding='utf-8')
    fout_test =open(os.path.join(corpora_output_dir,'test.csv'),"a",encoding='utf-8')
    fout_dev =open(os.path.join(corpora_output_dir,'dev.csv'),"a",encoding='utf-8')
    fout_full_train =open(os.path.join(corpora_output_dir,'train_full.csv'),"a",encoding='utf-8')
    csv_outputs = [fout_train,fout_test,fout_dev,fout_full_train]

    print(f"Collect csv train/test/dev/train_full...")
    all_wav_file_origin = []
    all_filenames =  set()
    for corpus_name  in corpus2collect:
        files = collect_all_csv(corpus_name,csv_outputs)
        ##unique name validation
        curr_filenames = set([f.split('/')[-1] for f in files])
        ##if intersection is not empty, is not unique names
        if(len(all_filenames & curr_filenames))>0:
            raise('not unique name, check it!')
        
        all_filenames.update(curr_filenames)
        #########################
        data_dir = corpus2collect_alt_dir.get(corpus_name,None)
        for f_rel in files:
            f_rel = f_rel.replace('/',os.path.sep)
            dataset_path = os.path.abspath(corpus_name) if data_dir==None else  os.path.join(data_dir, corpus_name)        
            origin_data_path = os.path.join(dataset_path, "origin") if data_dir==None else  data_dir
            wav_path = os.path.join(origin_data_path, f_rel) 
            all_wav_file_origin.append(wav_path)

    fout_train.close()
    fout_test.close()
    fout_dev.close()
    fout_full_train.close()
    ####################################
    ##copy file
    print(f"Collect Wav files...")
    pool = Pool()
    bar = progressbar.ProgressBar(max_value=len(all_wav_file_origin), widgets=SIMPLE_BAR)
    for i, _ in enumerate(pool.imap_unordered(_maybe_copy_one, all_wav_file_origin), start=1):
        bar.update(i)

    bar.update(len(all_wav_file_origin))
    pool.close()
    pool.join()
    ###########################################

def collect_all_csv(corpus_name,csv_outputs):

    data_dir = corpus2collect_alt_dir.get(corpus_name,None)
    dataset_dir = os.path.abspath(corpus_name)
    collect_csv(os.path.join(dataset_dir,'train.csv'),csv_outputs[0])
    collect_csv(os.path.join(dataset_dir,'test.csv'),csv_outputs[1])
    collect_csv(os.path.join(dataset_dir,'dev.csv'),csv_outputs[2])
    files = collect_csv(os.path.join(dataset_dir,'train_full.csv'),csv_outputs[3])

    return files


def collect_csv(csv1_path,file_output):
    f = open(csv1_path,encoding='utf-8')
    next(f) # skip the header    
    files = set()
    for line in f:
        wav_file_rel_path = line[0:line.find(',')]
        filename = wav_file_rel_path.split('/')[-1]
        if(wav_file_rel_path not in files):
            files.add(wav_file_rel_path)
        else:
            raise(f'not unique wav filename {wav_file_rel_path} - fix!')

        new_file_path = 'audios/'+filename
        new_line = line.replace(wav_file_rel_path,new_file_path)
        file_output.write(new_line)
    f.close() # not really needed
    return files

def _maybe_copy_one(origin_file_path):
    ##need repeat define var, progress bar  multiprocessor
    corpora_output_dir = os.path.abspath('collected_corpora')
    corpora_wav_output_dir = os.path.join(corpora_output_dir,'audios')
    filename = os.path.split(origin_file_path)[-1]

    dest_file = os.path.join(corpora_wav_output_dir,filename)
    if(os.path.isfile(dest_file)):
        ##file exist , skip
        return

    ##copy file
    copyfile(origin_file_path, dest_file)
    #################################
 
if __name__ == "__main__":
    collect_datasets()