class TextAnalyzer(object):
    """description of class"""

    import TextAnalysis

    #Class attributes
    company=""
    text=""
    link=""
    result=""
    #text_date=""  #Date de parution de l'article ou tweet extrait
    #date=""  #Date d'analyse 

    #Constructor
    def __init__(self, company, text, link):
        self.company=company
        self.text=text
        self.link=link

    #Instance Method
    def __str__(self):
        return "Company: "+self.company+"\nText: \n"+self.text+"\nFound on:"+self.link+"\nAnalysis result: "+self.result

    def toString(self):
        return "Company: "+self.company+" Analysis result: "+self.result

    def FindCompanyMentions(self): #Retourne les phrases mentionnant l'entreprise
        comp=[self.company]
        sentences=TextAnalysis.DetectSentences(self.text, comp)
        #print sentences
        return sentences

    def RunAnalysis(self):
        #Tout le traitement se fera ici, c'est un peu le main() de notre classe.
        result="<Analysis result>"


    



