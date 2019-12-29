#!/usr/bin/env python3

from typing import Pattern
import re
from pathlib import Path
from unidecode import unidecode  
import time

global start_time_regexp

mapping_normalization = [

  ## If the sentence start with a number, the sentence is removed
  [ re.compile('^\d+(.*)'), u'' ],  

  ## Remove the stuff inside ()[]{}
  [ re.compile('(\(|\[|{)[^(\)|\]|})]*(\)|\]|})'), u'' ],
  ##must be twice time for nested parentheses
  [ re.compile('(\(|\[|{)[^(\)|\]|})]*(\)|\]|})'), u'' ],
 
  ##remove uninteresting characters
  [ re.compile('\-|=|_|–|\+|\(|\||—|\)|\[|\]|~|\*|/|"|¨|\^'), u' ' ],     
  
  [ u'¢' , u'c' ],  
  
  ## Sanitize ... to . 
  # Attention: Ellipsis are part of grammar, they are punctuation, they should not be eliminated
  [ re.compile('\.+'), u'.' ],
  ##normalize spaces
  [ re.compile('\n|\t|\r|\s+'), u' ' ],

  ##accentate maiuscole
  [ re.compile('È'), u'e\'' ],

  ##Sanitize single apex
  [ re.compile('´|`|\'\''), u'\'' ],

  ## To avoid conflicts with single ' and accented letter we removed them
  [ re.compile('(\s|^)(\')([^\']*)(\')(\s|$)'), r'\3' ],

  ## remove char for those cases
  [ re.compile('(#\d+)|#|(\s°)'), u'' ],
  
  ## Sanitization for those cases
  [ u'n°' , u'numero ' ],  

  ## Sanitization for currency values
  [ re.compile('\$\s*([0-9]+[.,]{0,1}[0-9]*)'), r'\1 dollari' ], 
  [ re.compile('([0-9]+[.,]{0,1}[0-9]*)\s*\$'), r'\1 dollari' ],
  [ re.compile('(₤|£)\s*([0-9]+[.,]{0,1}[0-9]*)'), r'\2 lire' ], 
  [ re.compile('([0-9]+[.,]{0,1}[0-9]*)\s*₤'), r'\1 lire' ],
  [ re.compile('(€)\s*([0-9]+[.,]{0,1}[0-9]*)'), r'\2 euro' ], 
  [ re.compile('([0-9]+[.,]{0,1}[0-9]*)\s*€'), r'\1 euro' ],

  ##space trim - it must be reapplied again
  [ re.compile('\s+'), u' ' ]
]


mapping_normalization_after_decode = [

  ## Convert old fashion accented letter to the real accented letter
  [ u'E\' ', u'è ' ],
  [ re.compile('a\'(\s|$|,|\.|\?)'), r'à\1' ], 
  [ re.compile('e\'(\s|$|,|\.|\?)'), r'è\1' ],
  [ re.compile('i\'(\s|$|,|\.|\?)'), r'ì\1' ],
  [ re.compile('o\'(\s|$|,|\.|\?)'), r'ò\1' ],
  [ re.compile('u\'(\s|$|,|\.|\?)'), r'ù\1' ],     

]


def maybe_normalize(value, mapping=mapping_normalization):
  for norm in mapping:
    if(value==''):
      break

    if type(norm[0]) == str:
      value = value.replace(norm[0], norm[1])
    elif isinstance(norm[0], Pattern):
      try:
        value = norm[0].sub(norm[1], value)
      except Exception as e:
        raise(e)
    else:
      print('UNEXPECTED', type(norm[0]), norm[0])

  return value

def line_not_relevant(text):
  
  if(len(text)<2):
    return True

  
  ## If the sentence include those symbols we ignore it (is part of the opening subtitles)  
  if('®' in text
     or '©' in text
     or '±' in text):
    return True

  ##sentence with one word that contain those symbols, we ignore it
  if(not ' ' in text and 
    (   '_' in text
     or '@' in text
     or '}' in text     
     or '+' in text
     or '{' in text)):
     return True

  ##add other cases

  return False
 

def normalize_text(text):

  ## If the whole sentence is uppercase we convert to a lowercase version
  if(text.isupper()):
    text = text.lower()

  #normalization first step (replace and sub regex)
  text = maybe_normalize(text,mapping_normalization)

  ###### UNICODE/NO-ASCII CHAR
  ##Opensubtiles Dataset contains no-ASCII char
  ## instead of process single unicode case we use unidecode package to delegate all unicode char processing
  # to keep all vowels properly accented, and at the same time eliminate the other unicode characters, you need to use a substitution with place holders
  ##abstent unicode placeholder
  text =  text.replace('à', '<PH_A>')
  text =  text.replace('è', '<PH_E>')
  text =  text.replace('ì', '<PH_I>')
  text =  text.replace('ò', '<PH_O>')
  text =  text.replace('ù', '<PH_U>')

  text = unidecode(text)## # Transliterate an Unicode object into an ASCII string
  ###
  text =  text.replace('<PH_A>','à')
  text =  text.replace('<PH_E>','è')
  text =  text.replace('<PH_I>','ì')
  text =  text.replace('<PH_O>','ò')
  text =  text.replace('<PH_U>','ù')
  #############################################################
  
  ##normalization second step:  that produces output with unicode characters
  text = maybe_normalize(text,mapping_normalization_after_decode)

  text = text.strip()

  if(len(text)==0):
    return ''
  #################################
  ##other normalization step

  ##remove dot and apex only if at the beginning of sentence
  if(text[0]=='.' or text[0]=='\''): 
    text = text[1:len(text)]

  if(len(text)==0):
    return ''
  ##remove apex only if at the end of sentence
  if(text[len(text)-1]=='\''): 
    text = text[0:len(text)-1]  
  
  text = text.strip()

  return text


def preprocess_and_extract(folder,start_year=1920,split_output_file_rows=None,check_sentence_cleaning=False):  
  """ Excract text from opensubtitles dataset
      preprocessing text, lear and normalization

          :param folder: relative path of opensubtitles dataset : str
          :type folder: str
          :param start_year: start year filter
          :type start_year: int
          :param split_output_file_rows: Se diverso da None verranno generati più file di output ognuno con 'split_output_file_rows' numero di righe
          :type split_output_file_rows: int            
          :param check_sentence_cleaning: Debug flag, check the goodness of the regexp applied. After the cleaning and normalization step, check that the sentence contains only 'typical char' of a conversation.
          :type check_sentence_cleaning bool        
          :return: Nothing
          """

  pathlist = Path(folder).glob('**/*.xml')
  xml_file_list = []
  for path in pathlist:
      #path is object not string
      year_folder = str(path.parent.parent._parts[len(path.parent.parent._parts)-1])
      try:
        year_folder_int = int(year_folder)
        if(year_folder_int<1300 or year_folder_int>=start_year):
          xml_file_list.append(str(path))
      except:
        pass

  
  total_files = len(xml_file_list)
  print('total xml file: '+ str(total_files))

  file_output = None
  if(len(xml_file_list)>0):    
    file_output=open("opensubtiles_extracted.txt","w")

  count_file = 0
  count_sentence = 0
  count_split_file = 1
  global start_time_regexp
  start_time_regexp = time.time() 

  for xml_file_path in xml_file_list:
    try:

      ##decomment to test some sentence
      #if(count_sentence>=6000):
      #  break
      ####################

      fp = open(xml_file_path,encoding='utf-8')
      
      prev_time_line = None
      exported_file = False
      for line in fp:
        _line= line

        line=line.strip()
        if(line==''):
          continue
        ## If start with this symbol we ignore the line
        if(line[0]!='<'):
          ##clear and normalize
          line =  process_text(line)
          ##############
          if(line=='' or len(line)<2):
            continue
          
          if(check_sentence_cleaning):
            regexp_apex_ok = re.compile(r'\w\'\w')
            number_ok = re.compile(r'\d+°') ##example 1°, 2°,6°, 49°
            line_temp = line.replace(" ", "")
            if(not line_temp.isalnum() 
                and '!' not in line_temp 
                and '?' not in line_temp
                and '.' not in line_temp
                and ':' not in line_temp
                and ',' not in line_temp
                and ';' not in line_temp
                #and '"' not in line_temp 
                and not regexp_apex_ok.search(line_temp)
                and not number_ok.search(line_temp) ):
              print('IMPROVE TEXT CLEANING: ' + line + ' - source: '+_line) 
          #####################################################

          ## Generate multiple files if split_output_file_rows is enabled
          if split_output_file_rows!=None and not (count_sentence % split_output_file_rows):
            #count_sentence = 0
            file_output.close()
            new_filename = "opensubtiles_extracted_{}.txt".format(str(count_split_file))
            file_output=open(new_filename,"w")
            print('NEW FILE OUTPUT: ' + new_filename)
            count_split_file +=1
          ####
          try:
            ##decomment if you want to check input vs output
            #file_output.write(unidecode(_line))         
               
            file_output.write(line)
            file_output.write('\n')
            count_sentence +=1
          except Exception as e:
            raise(e)
          
          exported_file = True

        ##If it is important to separate sentences based on waiting breaks, 
        # decomment this... line with time tag start with '<time'
        #if(line.startswith('<time')):          
        #  prev_line = line
      
      if(exported_file):
        ##file exported line separator 
        file_output.write('\n')
    finally:
      fp.close()
      pass

    count_file +=1

    ##progress print
    if not (count_file % 100):
      print (count_file, '/', total_files, 'file processed')

  if(file_output!=None):
      file_output.close()

  print ('\n')
  print (count_sentence, ' sentences extracted.' )
  
def process_text(text):
  ##clear and normalize text
  text = text.strip()

  ##exclude line not relevant
  if(line_not_relevant(text)):
    return ''

  ##normalization
  text = normalize_text(text)

  return text

def test_regexp():
  
  #test cases found in opensubtitles dataset.

  #this function could be used for a test case of text processing (clear and normalization),
  #to be implemented better...

  test_pair = []
  test_pair.append(['Per cominciare... la civilta\' moderna e\' una truffa.','Per cominciare. la civiltà moderna è una truffa.'])
  test_pair.append(['£ 500 in premio per i ladri di cavalli','500 lire in premio per i ladri di cavalli'])
  test_pair.append(['{\pos(346372)}Agisco senza emozione','Agisco senza emozione'])
  test_pair.append(["Si', e' cosi'.",'Sì, è così.'])
  test_pair.append(["Si'... ",'Sì.'])
  test_pair.append(["testo ddjd(( -- )) - [ ok... ",'testo ddjd ok.'])
  test_pair.append(["Com'e?",'Com\'è?'])
 

  succ = True
  for pair in test_pair:
    text = pair[0]
    text_res =  process_text(text)
    text_expected = pair[1]
    if(text_res!=text_expected):
      print('error on text: {}'.format(text))
      print('output produced: {}'.format(text_res))
      print('output expected: {}'.format(text_expected)) 
      print('\n')
      succ = False
  
  if(succ):
    print('Processing successfully!!!!')

if __name__ == '__main__':

  ##decomment to run some test case on regexp expression
  #test_regexp()
  #############################

  folder_dataset = '../../../../../data_and_models/dataset/public_opensubtitle_sottotitoli_it_2018/it/OpenSubtitles/raw/it'
  start_year=1920

  ##the procedure produces a text file of several gigabytes.
  # If you want to have files that can be easily explored with Notepad++/Sublime I recommend splitting the output files into several files of about 1G each (about 34Milion sentence by file)
  split_output_file_rows = 34000000 ## 34 milion rows , 1G file txt

  #########################################

  start_time = time.time()  

  preprocess_and_extract(folder_dataset,start_year=start_year,split_output_file_rows=split_output_file_rows)

  print("--- %s seconds duration ---" % (time.time() - start_time))

  global start_time_regexp
  print("--- %s seconds duration regexp parsing ---" % (time.time() - start_time_regexp))
  
