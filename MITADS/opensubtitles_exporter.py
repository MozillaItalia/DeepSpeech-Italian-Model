#!/usr/bin/env python3

from typing import Pattern
import re
from pathlib import Path
from unidecode import unidecode  
import time


mapping_normalization = [

  ##L'Ordine delle entry (replace e sub con regex) è significativo!!!

  ##se la frase contiene parole con underscore o  @, allora non fa parte di una conversazione
  ##[ re.compile('(^|(.*\s))\w+(_|@|®|\+|\{|\})\w+((\s.*)|$)'), u'' ],

  ## If the sentence start with a number, the number is removed
  [ re.compile('^\d+(.*)'), u'' ],  

  ## Remove the stuff inside ()[]{}
  [ re.compile('(\(|\[|{)[^(\)|\]|})]*(\)|\]|})'), u'' ],

  ## potrebbero essere parentesi annidate(ci sono nel dataset), lo lancio due volte
  [ re.compile('(\(|\[|{)[^(\)|\]|})]*(\)|\]|})'), u'' ],

  #### testo compreso tra separatori 
  #[ re.compile('(\-|=)[^(\-|=)]*(\-|=)'), u'' ],
  
  ##replace caratteri, sono presenti nelle frasi
  [ u'-' , u' ' ],
  [ u'=' , u' ' ],
  [ u'_' , u' ' ],
  [ u'–' , u' ' ],##trattino differente  
  [ u'+' , u'' ],
  [ u'(' , u'' ],
  [ u'|' , u'' ],
  [ u'—' , u' ' ],  
  [ u')' , u'' ],
  [ u'[' , u'' ],
  [ u']' , u'' ],
  [ u'~' , u'' ],
  [ u'=' , u'' ],  
  [ u'*' , u'' ],  
  [ u'/' , u' ' ],  
  [ u'¢' , u'c' ],    
  ##apici doppi , rimuovo sempre    
  [ u'"' , u'' ],
  [ u'¨' , u'' ],
  [ u'^' , u'' ],
  
  
  ## Sanitize ... to .
  [ re.compile('\.+'), u'.' ],
  ##sigle e testi con punti
  [ re.compile('\n|\t|\r'), u' ' ],
  [ re.compile('\s+'), u' ' ],

  ##accentate maiuscole
  [ u'È' , u'è' ],
  [ u'E\'\s' , u'è' ],  

  ##apostrofi, sono presenti 
  [ u'´' , u'\'' ],
  [ u'`' , u'\'' ],
  [ u'\'\'' , u'\'' ],  

  ## To avoid conflicts with single ' and accented letter we removed them
  [ re.compile('(\s|^)(\')([^\']*)(\')(\s|$)'), r'\3' ],

  ## punteggiatura non significativa alla fine del testo  
  [ re.compile('(.*)(\.)$'), r'\2' ],

  ## Convert old fashion accented letter to the real accented letter
  [ re.compile('a\'(\s|$|,|\.|\?)'), r'à\1' ],
  [ re.compile('e\'(\s|$|,|\.|\?)'), r'è\1' ],
  [ re.compile('i\'(\s|$|,|\.|\?)'), r'ì\1' ],
  [ re.compile('o\'(\s|$|,|\.|\?)'), r'ò\1' ],
  [ re.compile('u\'(\s|$|,|\.|\?)'), r'ù\1' ],

  ## cancelletto con numero , presente nei titoli di apertura   
  [ re.compile('#\d+'), u'' ],
  [ re.compile('#|\s°'), u'' ], 

  ##alcune normalizzazioni con numeri. sono presenti, vedere se serve questo tipo di normalizzazione
  ##ISSUE: potrebbero esserci problemi con maschile e femminile, vedi 6° strada ad esempio
  [ u'1°' , u'primo' ],
  [ u'2°' , u'secondo' ],
  [ u'3°' , u'terzo' ],
  [ u'4°' , u'quarto' ],
  [ u'5°' , u'quinto' ],
  [ u'49°' , u'quarantanovesimo' ],
  
  ## Sanitization for those cases
  [ u'n°' , u'numero ' ],  

  ## Sanitization for currency values
  [ re.compile('\$\s*([0-9]+[.,]{0,1}[0-9]*)'), r'\1 dollari' ], 
  [ re.compile('([0-9]+[.,]{0,1}[0-9]*)\s*\$'), r'\1 dollari' ],
  [ re.compile('(₤|£)\s*([0-9]+[.,]{0,1}[0-9]*)'), r'\2 lire' ], 
  [ re.compile('([0-9]+[.,]{0,1}[0-9]*)\s*₤'), r'\1 lire' ],
  [ re.compile('(€)\s*([0-9]+[.,]{0,1}[0-9]*)'), r'\2 euro' ], 
  [ re.compile('([0-9]+[.,]{0,1}[0-9]*)\s*€'), r'\1 euro' ],
  ##trim spazi
  [ re.compile('\s+'), u' ' ]
]


def maybe_normalize(value, mapping=mapping_normalization):
  for norm in mapping:
    if type(norm[0]) == str:
      value = value.replace(norm[0], norm[1])
    elif isinstance(norm[0], Pattern):
      try:
        value = norm[0].sub(norm[1], value)
      except Exception as e:
        raise(e)
    else:
      print('UNEXPECTED', type(norm[0]), norm[0])

  ##remove markup tags...(non sono presenti nel dataset )
  #value = loads(value)

  return value

def line_not_relevant(text):
  ##implementare logiche di esclusione righe
  if(len(text)<2):
    return True

  return False


def clear_text(text):
  ##text = re.sub(r'[^\x00-\x7F]+',' ', text)  mi toglie anche le È

  #PER I CARATTERI UNICODE ho usato libreria unidecode, questi non servono più
  #text = text.replace('\u200b',' ')## ZERO WIDTH SPACE
  #text = text.replace(u'ε','e') ##GREEK SMALL LETTER EPSILON
  #text = text.replace(u'♪','') ## char ♪
  #text = text.replace(u'♫','') ## char ♫
  #text = text.replace(u'¶','') ## char ♫
  
  #text = text.sub(r'[^\x00-\x7F]+',' ', text_ret)
  
  text = text.strip()

  return text

def normalize_text(text):

  ## If the whole sentence is uppercase we convert to a lowercase version
  if(text.isupper()):
    text = text.lower()

  ##se una sentence contiene una sola parola con caratteri speciali 
  # ALLORA tutta la sentence viene esclusa (fa  parte dei titoli di testa)
  
  if(not ' ' in text and 
    (   '_' in text
     or '@' in text
     or '}' in text     
     or '+' in text
     or '{' in text)):
     return ''
  ## If the sentence include those symbols we ignore it
  if('®' in text
     or '©' in text
     or '±' in text):
    return ''

  #normalization (replace and sub regex)
  text = maybe_normalize(text,mapping_normalization)

  ######da spostare sulla clear?? vedere se spostando la chiamata non abbiamo side effect 
  # unidecode normalizza i caratteri speciali ascii (altrimenti andrebbe in errore la fase di scrittura su file con utf-8)
  text = unidecode(text)
  #################

  text = text.strip()

  if(len(text)==0):
    return ''
  #################################
  ##other normalization step

  ##rimuovo il punto a pice all'inizio della sentence
  if(text[0]=='.' or text[0]=='\''): 
    text = text[1:len(text)]

  if(len(text)==0):
    return ''

  ##rimuovo apice alla fine della sentence, apici singoli già trattati. Quelli interni alla sentence potrebbero essere significativi
  if(text[len(text)-1]=='\''): 
    text = text[0:len(text)-1]  
  
  text = text.strip()

  return text


def preprocess_and_extract(folder,start_year=1920,split_output_file_rows=None):  
  """ Excract text from opensubtitles dataset
      preprocessing text, lear and normalization

          :param folder: relative path of opensubtitles dataset : str
          :type folder: str
          :param start_year: start year filter
          :type start_year: int
          :param split_output_file_rows: Se diverso da None verranno generati più file di output ognuno con 'split_output_file_rows' numero di righe
          :type split_output_file_rows: int            
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
  for xml_file_path in xml_file_list:
    try:
      fp = open(xml_file_path,encoding='utf-8')
      
      prev_time_line = None
      exported_file = False
      for line in fp:
        _line= line

        #if('$' in _line):
        #  deb = 0

        line=line.strip()
        if(line=='' or len(line)<2):
          continue

        ##le linee con il testo delle frasi non iniziano con apertura/chiusura tag  
        if(line[0]!='<'):
          ##clear and normalize
          line =  process_text(line)
          ##############
          if(line=='' or len(line)<2):
            continue

          ##debug check - abilita se vuoi avere un output con le segnalazioni delle righe che richiedono attenzione o ulteriore pulizia
          if(False):
            regexp_apex_ok = re.compile(r'\w\'\w')
            line_temp = line.replace(" ", "")
            if(not line_temp.isalnum() 
                and '!' not in line_temp 
                and '?' not in line_temp
                and '.' not in line_temp
                and ':' not in line_temp
                and ',' not in line_temp
                and ';' not in line_temp
                #and '"' not in line_temp 
                and not regexp_apex_ok.search(line_temp) ):
              print('IMPROVE TEXT CLEANING: ' + line + ' - source: '+_line) 
          #####################################################

          ## Generate multiple files if split_output_file_rows is enabled
          if split_output_file_rows!=None and not (count_sentence % split_output_file_rows):
            count_sentence = 0
            file_output.close()
            file_output=open("opensubtiles_extracted_{}.txt".format(str(count_split_file)),"w")
            count_split_file +=1
          ####
          try:
            file_output.write(line+ '\n')
            count_sentence +=1
          except Exception as e:
            ###QUESTO CODICE SI PUO' ELIMINARE _ ADESSO NON VA PIU' IN ERRORE
            
            print('ERROR WRITE ROW - '+str(e) + ' - processed: ' +line + ' - source: '+_line)
            
            ##remove all non-ascii char
            line = re.sub(r'[^\x00-\x7F]+','', line)
            file_output.write(line+ '\n')
            count_sentence +=1
            #raise(e)
          
          exported_file = True

        ##prev_line to check delay time, todo.. 
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
      print (count_file, '/', total_files, 'file preprocessed')

  if(file_output!=None):
      file_output.close()


def process_text(text):
  ##clear text 
  text = clear_text(text)

  ##exclude line not relevant
  if(line_not_relevant(text)):
    return ''

  ##normalization
  text = normalize_text(text)

  return text

def test_regexp():
  ##£ 500 in premio per i ladri di cavalli
  text = "{\pos(346372)}Agisco senza emozione"
  text =  process_text(text)

  iii=0

if __name__ == '__main__':

  #test_regexp()
 
  folder_dataset = '../../../../../data_and_models/dataset/public_opensubtitle_sottotitoli_it_2018/it/OpenSubtitles/raw/it'
  start_time = time.time()
  
  preprocess_and_extract(folder_dataset)

  print("--- %s seconds duration ---" % (time.time() - start_time))
