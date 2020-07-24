from typing.re import Pattern
from utils.roman_numbers import do_roman_normalization
import utils.blacklist as blacklist
from bs4 import Tag, NavigableString


class Sanitization:
    """Various methods to clean the text to be used with DeepSpeech"""

    def __init__(self):
        self.default_mapping = blacklist.unicode_symbols + blacklist.other

    def maybe_normalize(self, value, mapping=[], roman_normalization=False, mapping_prepend=True):

        mapping = mapping + self.default_mapping if mapping_prepend else self.default_mapping+mapping

        for norm in mapping:
            if type(norm[0]) == str:
                value = value.replace(norm[0], norm[1])
            elif isinstance(norm[0], Pattern):
                value = norm[0].sub(norm[1], value)
            else:
                print('UNEXPECTED', type(norm[0]), norm[0])
        if roman_normalization:
            value = do_roman_normalization(value)
        return value


    def prepare_splitlines(self, text):
        text = text.replace('. ', ".\n")
        text = text.replace('... ', "\n")
        text = text.replace('? ', "\n")
        text = text.replace('! ', "\n")
        text = text.replace('– ', "\n")
        text = text.replace('─ ', "\n")
        text = text.replace('""', '"' + "\n" + '"')

        if isinstance(text, Tag):
            return text.prettify()
        else:
            return text

    def clean_single_line(self, value):
        if value.startswith(';') or value.startswith('–') or value.startswith('.') or value.startswith(':') or value.startswith('\'') or value.startswith('*') or value.startswith(') ') or value.startswith('< ') or value.startswith(',') or value.startswith('-'):
            value = value[1:]

        if value.startswith('"') and value.endswith('"'):
            value = value.replace('"', '')

        if value.endswith('–') or value.endswith('*'):
            value = value[:-1]

        if value.count('"') == 1:
            value = value.replace('"', "")

        if(value.isupper()):
            value = value.lower()

        value = value.strip()  # clean line from whitespace at the beginning / at the end

        return value
