"""list of substitutions that needs to me made, they can be either:
 - couple of strings (old, new)
 - regex (matching regex, sub string)"""

import re
# from https://stackoverflow.com/questions/6609895/efficiently-replace-bad-characters
utf8_symbols = [
    ['\xc2\x82', ''],         # High code comma
    ['\xc2\x84', ''],        # High code double comma
    ['\xc2\x85', ''],       # Tripple dot
    ['\xc2\x88', ''],         # High carat
    ['\xc2\x91', '\x27'],      # Forward single quote
    ['\xc2\x92', '\x27'],      # Reverse single quote
    ['\xc2\x93', ''],      # Forward double quote
    ['\xc2\x94', ''],      # Reverse double quote
    ['\xc2\x95', ''],
    ['\xc2\x96', ''],         # High hyphen
    ['\xc2\x97', ''],        # Double hyphen
    ['\xc2\x99', ''],
    ['\xc2\xa0', ' '],
    ['\xc2\xa6', ''],         # Split vertical bar
    ['\xc2\xab', ''],        # Double less than
    ['\xc2\xbb', ''],        # Double greater than
    ['\xc2\xbc', 'un quarto '],       # one quarter
    ['\xc2\xbd', 'un mezzo '],       # one half
    ['\xc2\xbe', 'tre quarti '],       # three quarters
    ['\xca\xbf', '\x27'],      # c-single quote
    ['\xcc\xa8', ''],          # modifier - under curve
    ['\xcc\xb1',  '']          # modifier - under line
]

unicode_symbols = [
    ['\x82', ''],
    ['\x84', ''],
    ['\x85', ''],
    ['\x88', ''],
    ['\x91', '\''],
    ['\x92', '\''],
    ['‘', ''],  # no ' for you
    #  ['´',''], disabled for ted
    ['\x93', ''],
    ['\x94', ''],
    ['\x95', ''],
    ['\x96', ''],
    ['\x97', ''],
    ['\x99', ''],
    ['\xa0', ''],
    ['\xa6', ''],
    ['\xab', ''],
    ['\xbb', ''],
    ['\xbc', 'un quarto '],       # one quarter
    ['\xbd', 'un mezzo '],       # one half
    ['\xbe', 'tre quarti '],       # three quarters
    ['\xbf', ''],
    ['\xa8', ''],
    ['\xb1', ''],
    ['«', ''],
    ['»', ''],
    ['×', ''],
    ['_', ''],
    ['-', ''],
    ['—', ''],
    ['* * * ', ''],
    ['↑', ''],
    ['♫', ''],
    ['♪', ''],
    ['∇', ''],
    ['₂', ''],  # maybe 'due' eg COdue?
    ['⁰', 'elevato zero'],
    ['¹', 'elevato uno'],
    ['²', ' al quadrato'],
    ['³', ' al cubo'],
    ['%', ' per cento'],
    ['˚', ''],  # esimo?
    ['τ', ''],
    ['π', ''],  # pigreco?
    ['§', ''],
    ['¤', ''],
    ['º', ''],
    ['°', ''],
    ['|', ''],
    ['/', ''],
    ['#', ''],
    ['¿', ''],
    ['@', ''],
    ['=', ''],
    ['…', ''],
    ['ʾ', ''],
    ['？', ''],
    ['™', ''],
    ['®', ''],
    ['©',''],
]


other = [
    ['( ', ''],
    [' , ', ', '],
    [' )', ''],
    [' .', '.'],
    #['\' ', '\''],
    [' !', '!'],
    [' ?', '?'],
    ['\'\'', ''],
    ['“', '"'],
    ['”', '"'],
    ['’', '\''],
    ['" "', '"'],
    [re.compile(r'^https?:\/\/.*[\r\n]*'), ''],
    [re.compile(r'^http?:\/\/.*[\r\n]*'), ''],
    [re.compile(r'(^[ \t]+|[ \t]+(?=:))'), ''],
    ['Sig. ', 'Signor '],
    ['Sr. ', 'Signor '],
    ['Sra. ', 'Signora '],
    [re.compile(r'\[\d+\]'), ''],
    ['  ', ' ']  # replaces double spaces with single one
]
