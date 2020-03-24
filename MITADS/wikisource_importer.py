#!/usr/bin/env python3
from urllib.request import Request, urlopen
from fake_useragent import UserAgent
from utils import sanitize, line_rules

validate_line = line_rules.LineRules()
clean_me = sanitize.Sanitization()


books = ['Le_lettere_di_Aldo_Moro_dalla_prigionia_alla_storia', 'Nigrizia/Editoriale_giugno_2011',
         'Il_manifesto_della_guerriglia_Open_Access', 'Le_donne_non_vi_vogliono_pi%C3%B9_bene',
         'A_proposito_di_Leonardo_e_della_sfera_del_fuoco/A_proposito_di_Leonardo_e_della_sfera_del_fuoco',
         'Lettera_a_Angelo_De_Gubernatis_(17_febbraio_1906)', 'Lettera_ai_giudici',
         'Lettera_ai_lavoratori_americani',
         'Lettera_ai_cappellani', 'Lettere_e_testimonianze_dei_ferrovieri_caduti_per_la_patria',
         'Ho_amore', 'Il_bacio_di_Lesbia', 'Il_cedro_del_Libano/Ferro_e_fuoco',
         'Il_mio_cuore_fra_i_reticolati/Un_uomo_del_passato', 'Il_mio_diario_di_guerra',
         'Il_tamburo_di_fuoco_(1960)',
         'Il_fermo_proposito', 'Il_romanzo_della_fanciulla', 'La_casa_del_poeta', 'La_casa_paterna',
         'La_cattedrale_e_il_bazaar', 'La_chiesa_della_solitudine', 'Memorie_infantili', 'Non_abbiamo_bisogno',
         'Orizzontale']
start = 1
download_link = 'https://tools.wmflabs.org/wsexport/tool/book.php?lang=it&format=txt&page='
result = open("./output/wikisource.txt", "w", encoding='utf-8')
print("Number of books to import: {}".format(len(books)))

ua = UserAgent()

for book in books:
    print("Processing book : {}\n {} of {}".format(book,start,len(books)))
    response = Request(download_link + book, headers={'User-Agent': ua.random})
    data = urlopen(response).read().decode('UTF-8')

    raw_text = clean_me.maybe_normalize(data.strip())
    raw_text = clean_me.splitlines(raw_text).splitlines()
    
    text = ''
    for sentences in raw_text:
        lines = sentences.split(".")
        for line in lines:
            line = clean_me.cleansingleline(line).strip()
            if len(line) <= 12:
                continue
            
            if line.isupper():
                continue
            
            if validate_line.contain(line, ['Â§', '=', '--', '~', 'wiki', 'licenses', '//', ' pp']):
                continue
            
            if line.find('/') >= 1:
                continue

            if validate_line.startswith(line, ['(', '...', ',', '[']):
                continue
            
            if validate_line.endswith(line, [' M', ' p', 'n', ' F']):
                continue
            
            if validate_line.isdigit([line, line[1:], line[:1]]):
                continue
            
            if validate_line.isbookref(line):
                continue
                
            if validate_line.isbrokensimplebracket(line):
                continue
            
            text += line + "\n"
            
    result.write(text)
    start += 1
    
result.close()

result = open('./output/wikisource.txt', 'r', encoding='utf-8')
print('Number of lines: ' + str(len(result.read().splitlines())))
result.close()
