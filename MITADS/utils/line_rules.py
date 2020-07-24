import re
import json
valid_char_regex = re.compile(r"[^\s'abcdefghijklmnopqrstuvwxyzàèéìíòóôùúABCDEFGHIJKLMNOPQRSTUVWXYZÀÈÉÌÍÒÓÔÙÚ,.!?:;]")


class LineRules:
    """Rules to identify a valid line
    Lines Rules has the ability to automatically log the discarded sentences in a json file.
    To use it you need to pass a file path to the __init__ and then call save when you have finished to write to disk.
    The file is a dict where keys are the rule and values are a list of discarded sentences"""


    def __init__(self, discard_file=None):
        """provide a file path to have a place where to save discarded sentences"""
        self.discard_file = discard_file
        if discard_file:
            self.discarded = {}

    def discard(self, rule, line):
        if self.discard_file:
            self.discarded.setdefault(rule, []).append(line)

    def save(self):
        with open(self.discard_file, 'w') as f:
            json.dump(self.discarded, f)

    def is_not_valid(self, line):
        not_valid = valid_char_regex.search(line)
        if not_valid: self.discard("is_not_valid", line)
        return not_valid
    
    def startswith(self, line, chars):
        for char in chars:
            if line.startswith(char):
                self.discard("startswith_" + str(chars) , line)
                return True
            
    def endswith(self, line, chars):
        for char in chars:
            if line.endswith(char):
                self.discard("endswith_" + str(chars), line)
                return True
    
    def contain(self, line, chars):
        for char in chars:
            if line.find(char) >= 0:
                self.discard("contain" + str(chars), line)
                return True
    
    def isdigit(self, searchme):
        for search in searchme:
            if search.isdigit():
                self.discard("is_digit", search)
                return True
            
    def isbookref(self, text):
        text = text.replace('.', '')
        if text.find(',') >= 2 and text[-2:].isdigit():
            self.discard("isbookref", text)
            return True
        
    def isbrokensimplebracket(self, text):
        if text.find('(') >= 1 and text.find(')') == -1:
            self.discard("isbrokensimplebracket", text)
            return True
        
    def isbrokenparenthesis(self, text):
        if text.find(')') >= 1 and text.find('(') == -1 or text.find('(') >= 1 and text.find(')') == -1:
            self.discard("isbrokenparenthesis", text)
            return True
        
    def hasafinalrepeated(self, text):
        for word in text.split():
            if len(word) >= 2 and not word.strip().isnumeric():
                end = word[-3:]
                if len(end.replace(end[0], '')) == 0:
                    self.discard("hasafinalrepeated", text)
                    return True
        return False
    
    def parenthesismatch(self, text):
        last = None
        for char in text:
            if char == '(':
                if last is None or last == ')':
                    last = char
                elif last == '(':
                    return False
            elif char == ')':
                if last == '(':
                    last = char
                elif last is None or last == ')':
                    return False

        self.discard("parenthesismatch", text)
        return True