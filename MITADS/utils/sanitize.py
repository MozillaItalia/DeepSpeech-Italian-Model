from typing.re import Pattern
import roman
import re

class Sanitization:
    """Various methods to clean the text to be used with DeepSpeech"""
    
    def maybe_normalize(self, value, mapping='', roman_normalization=True):
      default_mapping = [
              [ u'«', u'' ],
              [ u'»', u'' ],
              [ u'×' , u'' ],
              [ u'_' , u'' ],
              [ u'-' , u'' ],
              [ u'—' , u'' ],
              [ u'* * * ' , u'' ],
              [ u'( ' , u'' ],
              [ u' , ' , u', ' ],
              [ u' )' , u'' ],
              [ u'Sig. '   , u'Signor ' ],
              [ re.compile('\[\d+\]'), u'' ],
            ]
      if mapping == '':
          mapping = default_mapping
      else:
          mapping = mapping + default_mapping
          
      for norm in mapping:
        if type(norm[0]) == str:
          value = value.replace(norm[0], norm[1])
        elif isinstance(norm[0], Pattern):
          value = norm[0].sub(norm[1], value)
        else:
          print('UNEXPECTED', type(norm[0]), norm[0])
    
      if roman_normalization:
          for ro_before, ro_after, ro in self.getRomanNumbers(value):
            try:
              value = value.replace(ro_before + ro + ro_after, ro_before + str(roman.fromRoman(ro)) + ro_after)
            except roman.InvalidRomanNumeralError as ex:
              print(ex)
              pass
    
      value = self.cleansingleline(value)
      
      return value.replace('  ', " ")
    
    
    def getRomanNumbers(self, ch):
      ROMAN_CHARS = "XVI"
      ro  = ''
      ros = 0
      for i in range(len(ch)):
        c = ch[i]
        if c in ROMAN_CHARS:
          if len(ro) == 0 and not ch[i-1].isalpha():
            ro  = c
            ros = i
          else:
            if len(ro) > 0 and ch[i-1] in ROMAN_CHARS:
              ro += c
        else:
          if len(ro) > 0:
            if not c.isalpha():
              yield ch[ros-1], ch[i], ro
            ro  = ''
            ros = i
    
      if len(ro) > 0:
        yield ch[ros-1], '', ro
        
    def splitlines(self, text):
        text = text.replace('. ', ".\n")
        text = text.replace('... ', "\n")
        text = text.replace('? ', "\n")
        text = text.replace('! ', "\n")
        text = text.replace('– ', "\n")
        text = text.replace('""', '"' + "\n" + '"')
        return text
    
    def escapehtml(self, text, html_escape_table=''):
        if html_escape_table == '':
            html_escape_table = {
                 "&amp;": "&",
                 '&quot;': '"',
                 "&apos;": "'",
                 "&gt;": ">",
                 "&lt;": "<",
                 "&Egrave;": "È",
                 }
        return "".join(html_escape_table.get(c,c) for c in str(text))
    
    def cleansingleline(self, value): 
      if value.startswith(';') or value.startswith('–'):
          value = value[1:]

      if value.startswith('"') and value.endswith('"'):
          value = value.replace('"', '')
          
      if value.endswith('–'):
          value = value[:-1]

      if value.count('"') == 1:
          value = value.replace('"', "")
    
      return value