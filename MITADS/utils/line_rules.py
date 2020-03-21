

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