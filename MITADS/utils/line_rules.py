

class LineRules:
    """Rules to identify a valid line""" 
    
    def startswith(self, line, chars):
        for char in chars:
            if line.startswith(char):
                return True
            
    def endswith(self, line, chars):
        for char in chars:
            if line.endswith(char):
                return True
    
    def contain(self, line, chars):
        for char in chars:
            if line.find(char) >= 0:
                return True
    
    def isdigit(self, searchme):
        for search in searchme:
            if search.isdigit():
                return True
            
    def isbookref(self, text):
        text = text.replace('.', '')
        if text.find(',') >= 2 and text[-2:].isdigit():
            return True
        
    def isbrokensimplebracket(self, text):
        if text.find('(') >= 1 and text.find(')') == -1:
            return True
        
    def isbrokenparenthesis(self, text):
        if text.find(')') >= 1 and text.find('(') == -1 or text.find('(') >= 1 and text.find(')') == -1:
            return True
        
    def hasafinalrepeated(self, text):
        for word in text.split():
            if len(word) >= 2 and not word.strip().isnumeric():
                end = word[-3:]
                if len(end.replace(end[0], '')) == 0:
                    return True
        return False
    
    def parenthesisnotmatch(self, text):
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
        return True