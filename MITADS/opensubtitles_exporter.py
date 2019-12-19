#!/usr/bin/env python3

from typing import Pattern
import re
from pathlib import Path

# Download and extract from  http://opus.nlpl.eu/download.php?f=OpenSubtitles/v2018/raw/it.zip

html_escape_table = {
     "&amp;": "&",
     '&quot;': '"',
     "&apos;": "'",
     "&gt;": ">",
     "&lt;": "<",
     }


mapping_normalization = [
  ##se la frase contiene parole con underscore, allora non fa parte di una conversazione
  [ re.compile('(^|(.*\s))\w+_\w+((\s.*)|$)'), u'' ],
    
  ##tutto ciò è contenuto tra paretesi va eliminato, non fa parte di una conversazione    
  [ re.compile('(\(|\[|{)[^(\)|\]|})]*(\)|\]|})'), u'' ],
  [ re.compile('(\-|=)[^(\-|=)]*(\-|=)'), u'' ],
  ##se la frase inizia con un numero , viene eliminata
  [ re.compile('^\d+(.*)'), u'' ],
  [ u'-' , u'' ],
  [ u'+' , u'' ],
  [ u'(' , u'' ],
  #[ u' , ' , u', ' ],
  [ u')' , u'' ],
  [ u'[' , u'' ],
  [ u']' , u'' ],
  [ u'~' , u'' ],
  [ u'=' , u'' ],  
  [ u'*' , u'' ],  
  [ u'È' , u'è' ],
  [ u'E\'\s' , u'è' ],  
  [ u'/' , u' ' ],  
  [ u'¢' , u'c' ],    
  ##apici doppi , rimuovo sempre    
  [ u'"' , u'' ], 
  ##sequenza di punti
  [ re.compile('\.+'), u'.' ],
  ##sigle e testi con punti
  [ re.compile('\n|\t|\r'), u' ' ],
  [ re.compile('\s+'), u' ' ],

   ##testi racchiusi tra apici singoli - in conflitto con le accentate, rimuovo questo tipo di apici
  [ re.compile('^(\')(.*)(\')$'), r'\2' ],

  ## punteggiatura non significativa alla fine del testo  
  [ re.compile('(.*)(\.)$'), r'\2' ],
  ##normalizziamo vovcali accentate
  [ re.compile('a\'(\s|$|,|\.|\?)'), r'à\1' ],
  [ re.compile('e\'(\s|$|,|\.|\?)'), r'è\1' ],
  [ re.compile('i\'(\s|$|,|\.|\?)'), r'ì\1' ],
  [ re.compile('o\'(\s|$|,|\.|\?)'), r'ò\1' ],
  [ re.compile('u\'(\s|$|,|\.|\?)'), r'ù\1' ],
  [ re.compile('#\d+'), u'' ],
  [ u'#' , u'' ],
  [ u'1°' , u'primo' ],
  [ u'2°' , u'secondo' ],
  [ u'3°' , u'terzo' ],
  [ u'5°' , u'quinto' ],
  [ u'n°' , u'numero ' ],
  
  [ re.compile('\s+'), u' ' ]
]


def maybe_normalize(value, mapping=mapping_normalization):
  for norm in mapping:
    if type(norm[0]) == str:
      value = value.replace(norm[0], norm[1])
    elif isinstance(norm[0], Pattern):
      value = norm[0].sub(norm[1], value)
    else:
      print('UNEXPECTED', type(norm[0]), norm[0])
  ##remove markup tags
  #value = loads(value)
  return value

def line_not_relevant(text):

  if(len(text)<2):
    return True

  return False


def clear_text(text):
  ##text = re.sub(r'[^\x00-\x7F]+',' ', text)  mi toglie anche È

  text = text.replace('\u200b',' ')## ZERO WIDTH SPACE
  text = text.replace(u'ε','e') ##GREEK SMALL LETTER EPSILON
  text = text.replace(u'♪','') ## char ♪
  text = text.replace(u'♫','') ## char ♫
  #text = text.sub(r'[^\x00-\x7F]+',' ', text_ret)
  
  text = text.strip()

  return text

def preprocess_text(text):

  ##SOLO SE  tutto il testo è upper case allora va portato lower case
  if(text.isupper()):
    text = text.lower()

  #normalization
  text = maybe_normalize(text,mapping_normalization)

  if(len(text)==0):
    return ''
  #################################
  ##other normalization step
  if(text[0]=='.'): 
    text = text[1:len(text)]
  text = text.strip()
  return text

def preprocess_and_extract(folder,start_year=1921):  

  pathlist = Path(folder).glob('**/*.xml')
  xml_file_list = []
  for path in pathlist:
      #path is object not string
      year_folder = str(path.parent.parent._parts[len(path.parent.parent._parts)-1])
      try:
        year_folder_int = int(year_folder)
        if(year_folder_int<1300 or year_folder_int>start_year):
          xml_file_list.append(str(path))
      except:
        pass
      #if(len(xml_file_list)>3000) :
      #  break

  
  total_files = len(xml_file_list)
  print('total xml file: '+ str(total_files))

  file_output = None
  if(len(xml_file_list)>0):    
    file_output=open("opensubtiles_extracted.txt","w")

  count_file = 0
  for xml_file_path in xml_file_list:
    try:
      fp = open(xml_file_path,encoding='utf-8')
      
      prev_time_line = None
      exported_file = False
      for line in fp:
        _line= line

        #if('Tutti pronti ad andare' in _line):
        #  deb = 0
        line=line.strip()
        if(line[0]!='<'):
          ##clear text 
          line = clear_text(line)

          if(line==''):
            continue
          ##exclude line     
          if(line_not_relevant(line)):
            continue

          line = preprocess_text(line)

          if(line==''):
            continue

          ##debug check
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
                and '"' not in line_temp 
                and not regexp_apex_ok.search(line_temp) ):
              print('IMPROVE TEXT CLEANING: ' + line)

          ####
          try:
            file_output.write(line+ '\n')
          except Exception as e:
            print('ERROR WRITE ROW - '+str(e) + ' - source: ' +line)
            ##remove all non-ascii char
            line = re.sub(r'[^\x00-\x7F]+','', line)
            file_output.write(line+ '\n')
            #raise(e)
          exported_file = True

        ##prev_line to check delay time, todo.. 
        if(line.startswith('<time')):          
          prev_line = line
      
      if(exported_file):
        ##file exported line separator 
        file_output.write('\n')
    finally:
      fp.close()
      pass
    count_file +=1
    if not (count_file % 100):
      print (count_file, '/', total_files, 'file preprocessed')

  if(file_output!=None):
      file_output.close()


if __name__ == '__main__':

  folder = 'C:\\ezioDev\\data_and_models\\dataset\\public_opensubtitle_sottotitoli_it_2018\\it\\OpenSubtitles\\raw\\it'
  preprocess_and_extract(folder)



