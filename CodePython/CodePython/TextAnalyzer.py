import TextAnalysis
from datetime import datetime

class TextAnalyzer(object):
    """description of class"""

    #Class attributes
    Id=0

    #Constructor
    def __init__(self, company, text, link, text_date):
        TextAnalyzer.Id+=1
        self.id=TextAnalyzer.Id
        if company[0].islower():
            company.capitalize()
        self.company=company
        self.text=text
        self.link=link
        self.text_date=text_date
        self.status=0 #0 si RAS, 1 sinon
        self.result=""
        self.date=""
        self.crit_sents=[] #Phrase qui ont soulevé l'alerte. Si le statut est de 1, cette variable ne peut être vide. 

    #Instance Method
    def __str__(self):
        if((self.link).startswith("https://twitter.com")):
            return "Id: "+str(self.id)+"\nCompany: "+self.company+"\nText: "+self.text+"\n\nFound on:"+self.link+"\nTweet date: "+str(self.text_date)+"\nAnalysis date: "+str(self.date)+ \
            "\nStatus: "+str(self.status)+"\nAnalysis result: "+self.result
        else:
            return "Id: "+str(self.id)+"\nCompany: "+self.company+"\nText: "+self.text+"\n\nFound on:"+self.link+"\nArctile date: "+str(self.text_date)+"\nAnalysis date: "+str(self.date)+ \
            "\nStatus: "+str(self.status)+"\nAnalysis result: "+self.result

    def toString(self):
        return "Company: "+self.company+" Analysis result: "+self.result

    def FindCompanyMentions(self): #Retourne les phrases mentionnant l'entreprise
        comp=[self.company]
        sentences=TextAnalysis.DetectSentences(self.text, comp)
        #print sentences
        return sentences

    def RunAnalysis(self):  #Tout le traitement se fera ici, c'est un peu le main() de notre classe.
        self.date=datetime.now()
        compsentences=TextAnalysis.DetectSentences(self.text, [self.company]) #phrases où est mentionnée l'entreprise
        for sentence_index in compsentences:
            #print(str(compsentences[sentence_index]))
            subj=TextAnalysis.IdentifySubject(str(compsentences[sentence_index]))
            #print("Subject: "+str(subj))
            for kw in TextAnalysis.keywords:
                if kw in str(compsentences[sentence_index]):
                    self.status=1
                    self.result="Alert raised."
                    critical_sentence=str(compsentences[sentence_index])
                    self.crit_sents.append(critical_sentence)
        if(self.status==1):
            print("An alert has been raised.")

    if __name__=="__main__":
        #Test()
        print("")


