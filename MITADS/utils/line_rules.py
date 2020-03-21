

class LineRules:
    """Rules to identify a valid line""" 
    
    def startswith(self, line, chars):
        for char in chars:
            if line.startswith(char):
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
        if text.find(',') == 2 and text[-4:].isdigit():
            return True
        
    def isbrokensimplebracket(self, text):
        if text.find('(') >= 1 and text.find(')') == -1:
            return True