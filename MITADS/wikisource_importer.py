#!/usr/bin/env python3
import time
from urllib.request import Request, urlopen
from fake_useragent import UserAgent
from typing import Pattern
import roman
import re


def maybe_normalize(value, mapping):
    for norm in mapping:
        if type(norm[0]) == str:
            value = value.replace(norm[0], norm[1])
        elif isinstance(norm[0], Pattern):
            value = norm[0].sub(norm[1], value)
        else:
            print('UNEXPECTED', type(norm[0]), norm[0])
    for ro_before, ro_after, ro in getRomanNumbers(value):
        try:
            value = value.replace(ro_before + ro + ro_after, ro_before + str(roman.fromRoman(ro)) + ro_after)
        except roman.InvalidRomanNumeralError as ex:
            print(ex)
            pass
    if value.startswith(';'):
        value = value[1:]
    return value.replace('  ', " ")


def getRomanNumbers(ch):
    ROMAN_CHARS = "XVI"
    ro = ''
    ros = 0
    for i in range(len(ch)):
        c = ch[i]
        if c in ROMAN_CHARS:
            if len(ro) == 0 and not ch[i-1].isalpha():
                ro = c
                ros = i
            else:
                if len(ro) > 0 and ch[i-1] in ROMAN_CHARS:
                    ro += c
        else:
            if len(ro) > 0:
                if not c.isalpha():
                    yield ch[ros-1], ch[i], ro
                ro = ''
                ros = i
    if len(ro) > 0:
        yield ch[ros-1], '', ro


def main():
    mapping = [
        [u'«', u''],
        [u'»', u''],
        [u'', u''],
        [u'_', u''],
        [u'-', u''],
        [u'â', u''],
        [u'* * * ', u''],
        [u'( ', u''],
        [u' , ', u', '],
        [u' )', u''],
        [u'Sig. ', u'Signor '],
        [re.compile('\[\d+\]'), u''],
    ]
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
    file = open("wikisource.txt", "w", encoding='utf-8')
    print("Number of books to import: {}".format(len(books)))
    print("New file txt created to store content")
    ua = UserAgent()
    for book in books:
        print("Processing book : {}\n {} of {}".format(book,start,len(books)))
        response = Request(download_link + book, headers={'User-Agent': ua.random})
        data = urlopen(response).read().decode('UTF-8')
        data.strip()
        lines = data.splitlines()
        for line in lines:
            line.strip()
            sentences = line.split(".")
            for sentence in sentences:
                sentence = maybe_normalize(sentence, mapping)
                if len(sentence) <= 25:
                    continue
                if sentence.isupper():
                    continue
                if sentence.startswith('(') or sentence.startswith('...'):
                    continue
                if sentence.find('Â§') >= 0 or sentence.find('=') >= 0 or sentence.find('--') >= 0 or sentence.find('~') >= 0:
                    continue
                if sentence.strip().isdigit() or sentence.strip()[1:].isdigit() or sentence.strip()[:1].isdigit():
                    continue
                file.write(sentence+"\n")
        start+=1
    file.close()
    print("Processing finished and file closed")
    result = open('wikisource.txt', 'r', encoding='utf-8')
    print('Number of words in the new file: ' + str(len(result.read().split())))
    result.close()


if __name__ == "__main__":
    start_time = time.clock()
    main()
    print("--- %s seconds ---" % (time.clock() - start_time))
