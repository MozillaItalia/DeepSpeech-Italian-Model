
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
    ['\xc2\xa0', ''],
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
    [u'\x82', u''],
    [u'\x84', u''],
    [u'\x85', u''],
    [u'\x88', u''],
    [u'\x91', u'\''],
    [u'\x92', u'\''],
    [u'‘', u''],  # no ' for you
    #  [u'´',u''], disabled for ted
    [u'\x93', u''],
    [u'\x94', u''],
    [u'\x95', u''],
    [u'\x96', u''],
    [u'\x97', u''],
    [u'\x99', u''],
    [u'\xa0', u''],
    [u'\xa6', u''],
    [u'\xab', u''],
    [u'\xbb', u''],
    [u'\xbc', 'un quarto '],       # one quarter
    [u'\xbd', 'un mezzo '],       # one half
    [u'\xbe', 'tre quarti '],       # three quarters
    [u'\xbf', u''],
    [u'\xa8', u''],
    [u'\xb1', u''],
    [u'«', u''],
    [u'»', u''],
    [u'×', u''],
    [u'_', u''],
    [u'-', u''],
    [u'—', u''],
    [u'* * * ', u''],
    [u'↑', u''],
    [u'♫', u''],
    [u'♪', u''],
    [u'∇', u''],
    [u'₂', u''],  # maybe 'due' eg COdue?
    [u'⁰', u'elevato zero'],
    [u'¹', u'elevato uno'],
    [u'²', u' al quadrato'],
    [u'³', u' al cubo'],
    [u'%', u' per cento'],
    [u'˚', u''],  # esimo?
    [u'τ', u''],
    [u'π', u''],  # pigreco?
    [u'§', u''],
    [u'¤', u''],
    [u'º', u''],
    [u'°', u''],
    [u'|', u''],
    [u'/', u''],
    [u'#', u''],
    [u'¿', u''],
    [u'@', u''],
    [u'=', u''],
    [u'…', u''],
    [u'ʾ', u''],
    [u'？', u''],
    [u'™', u''],
    [u'®', u''],
    [u'©',u''],
]


other = [
    [u'( ', u''],
    [u' , ', u', '],
    [u' )', u''],
    [u' .', u'.'],
    #[u'\' ', u'\''],
    [u' !', u'!'],
    [u' ?', u'?'],
    [u'\'\'', u''],
    [u'“', u'"'],
    [u'”', u'"'],
    [u'’', u'\''],
    [u'" "', u'"'],
    [r'^https?:\/\/.*[\r\n]*', ''],
    [r'^http?:\/\/.*[\r\n]*', ''],
    [r'(^[ \t]+|[ \t]+(?=:))', ''],
    [u'Sig. ', u'Signor '],
    [u'Sr. ', u'Signor '],
    [u'Sra. ', u'Signora '],
    [re.compile('\[\d+\]'), u''],
]
