import roman
import re

ROMAN_NUM_PATTERN = re.compile(r" M{0,1}D{0,1}C{0,}I{0,1}X{0,}I{0,1}V{0,}I{2,} ")


def do_roman_normalization(sentence):
    find_roman = ROMAN_NUM_PATTERN.findall(sentence)
    for roman_num in find_roman:
        try:
            sentence = re.sub(
                roman_num, " " + str(roman.fromRoman(roman_num.strip()))+" ", sentence)
        except roman.InvalidRomanNumeralError as ex:
            print(ex)
            pass

    return sentence
    # old code
    # for ro_before, ro_after, ro in self.get_roman_numbers(value):
    #     try:
    #         value = value.replace(
    #             ro_before + ro + ro_after, ro_before + str(roman.fromRoman(ro)) + ro_after)
    #     except roman.InvalidRomanNumeralError as ex:
    #         print(ex)
    #         pass



def get_roman_numbers(ch):
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
