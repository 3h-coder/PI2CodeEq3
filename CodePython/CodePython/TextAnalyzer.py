class TextAnalyzer(object):
    """description of class"""

    import TextAnalysis

    #Class attributes
    company=""
    text=""
    result=""

    #Constructor
    def __init__(self, company, text):
        self.company=company
        self.text=text

    #Instance Method
    def __str__(self):
        return "Company: "+company+"\nText: \n"+text+"\nAnalysis result: "+result

    def toString(self):
        return "Company: "+company+" Analysis result: "+result

    def RunAnalysis(self):
        #Tout le traitement se fera ici, c'est un peu le main() de notre classe.
        result="<Analysis result>"



    



