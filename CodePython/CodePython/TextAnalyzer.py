from numpy import False_, True_
import TextAnalysis
from datetime import datetime
from datetime import timedelta
from datetime import date
import os

class TextAnalyzer(object):
    """
    The TextAnalyser object is meant to read a block of text and determine whether the specified company is in a state of danger, attack or neither.

    Instance attributes
    -------------
    company: str
        The company name of which we are trying to check the security status.
    text: str
        The block of text that needs to be analyzed, it can be an article or a tweet.
    link: str
        The link from which the text was extracted.
    text_date: date
        The date on which the text was written.
    status: int
        A number that indicates the company security status.
        For example, a company that is safe will have a status equal to 0, whereas one where the occurence of an attack
        is certain will have a status equal to 3.
    result: str
        The status description after analysis.
    date: datetime
        Date and time of analysis.   
    crit_sents: list[str]
        List of sentences that led to raising an alert. If the status is > 0, this variable cannot be empty.
    
    Class attributes
    -------------
    Id: int
        The indentifier of the created TextAnalyzer object.
    """
    #Class Methods
    def LoadWordDic(filepath):
        """
        Loads the dictionnary of keywords that we will use to extract the sentences to compare.
        Returns a list of words (strings).

        Parameter
        -------------
        filepath: str
            Absolute or relative path to the file containing all the keywords we will use for extraction.
        """
        WordDic=[]
        with open (filepath,"r") as file:
            for line in file:
                WordDic.append(line.rstrip())
        return WordDic

    def LoadSentenceDic(filepath, company):
        """
        Loads the dictionnary of sentences that we will use to compare the text sentences to.
        Returns a list of sentences (strings).

        Parameters
        -------------
        filepath: str
            Absolute or relative path to the file containing all the sentences we will use for comparison.
            (One line corresponds to one sentence)

        company: str
            The company name of which we are trying to check the security status.
        """
        SentDic=[]
        with open (filepath,"r") as file:
            for line in file:
                if "CompName" in line:
                    line=line.replace("CompName", company.lower())
                SentDic.append(line.rstrip())
        return SentDic

    def LoadID():
        """
        Reads the ta_count.txt file to retreive the number of TextAnalyzer objects created.
        This class method is meant to update the ID when creating a new TextAnalyzer object.
        """
        with open ("analyzer_tools/ta_count.txt", "r") as file:
            count=int(file.readline().rstrip())
        return count

    def SaveID():
        """
        Saves the updated Id variable into the ta_count.txt file.
        """
        with open ("analyzer_tools/ta_count.txt", "w") as file:
            file.write(str(TextAnalyzer.Id))

    #Class attributes
    Id=0
    wordDic=LoadWordDic("analyzer_tools/Keyword_dictionnary.txt")

    #Constructor
    def __init__(self, company, text, link, text_date):
        TextAnalyzer.Id=TextAnalyzer.LoadID()+1
        TextAnalyzer.SaveID()
        self.id=TextAnalyzer.Id
        if company[0].islower():
            company.capitalize()
        self.company=company
        self.text=text
        self.link=link 
        self.text_date=text_date 
        self.status=-1 
        self.result=""  
        self.date="" 
        self.crit_sents=[]



    #Instance Method
    def __str__(self):
        if((self.link).startswith("https://twitter.com")):
            return "Id: "+str(self.id)+"\nCompany: "+self.company+"\nText: "+self.text+"\n\nFound on:"+self.link+"\nTweet date: "+str(self.text_date)+"\nAnalysis date: "+str(self.date)+ \
            "\nStatus: "+str(self.status)+"\nAnalysis result: "+self.result+"\nCritical sentences:\n"+str(self.crit_sents)
        else:
            return "Id: "+str(self.id)+"\nCompany: "+self.company+"\nText: "+self.text+"\n\nFound on:"+self.link+"\nArctile date: "+str(self.text_date)+"\nAnalysis date: "+str(self.date)+ \
            "\nStatus: "+str(self.status)+"\nAnalysis result: "+self.result+"\nCritical sentences:\n"+str(self.crit_sents)

    def toString(self):
        return "Company: "+self.company+" Analysis result: "+self.result

    def FindCompanyMentions(self):
        """
        Searches for the sentences mentionning the company in the text.
        Returns them in a list.
        """
        sentences=TextAnalysis.DetectSentences(self.text, [self.company])
        #print sentences
        return sentences


    def RunAnalysis(self, wordDic=[], sentDic=[]):
        """
        Analyzes the text variable to update the status, result, date and crit_sents variables.

        Parameters
        -------------
        wordDic: list[str]
            List of keywords from which we will search specific sentences.
            (These keywords belong to the cyber attack lexical field.)

        sentDic: list[str]
            List of sentences we will use to compare the text sentences and raise an alert based on the similarity.
            (The sentences in this variable are typically the ones that would make us raise a level 3 alert.)
        """
        if wordDic==[]: 
            wordDic=TextAnalyzer.wordDic
        if sentDic==[]:
            sentDic=TextAnalyzer.LoadSentenceDic("analyzer_tools/Sentence_dictionnary.txt", self.company)
        self.date=datetime.now()
        self.status=0 #Default status
        self.result="Nothing to report." #Default result
        compsentences=TextAnalysis.DetectSentences(self.text, [self.company]) #First, we start by extracting the sentences where the company is mentionned. 
        for sentence in compsentences:
            sentence_status=0
            sentence_copy=str(sentence).lower() #To simplify the comparison process, all compared sentences will be in lowercase.
            date_too_old=False #We then check whether the sentence mentions an event that has occured more than a week prior to the article/tweet date.
            DetectedDates=TextAnalysis.IdentifyDateSentence(sentence_copy, datetime.combine(self.text_date, datetime.min.time()))
            for date in DetectedDates:
                if date < self.text_date-timedelta(days=7):
                    date_too_old=True
            if date_too_old==False: #We only proceed to the rest of the analysis if the date found is not considered as too old.
                for word in wordDic: #We now browse our word Dictionnary
                    if word in sentence_copy: #To check if the sentence also countains one of these words.
                        sentence_status=1
                        break #We do not need to check whether the sentence contains other words from the dictionnary as we will not save it more than once.
                if(sentence_status>=1): #We now proceed to further/deeper analysis
                    for example_sentence in sentDic:
                        score=TextAnalysis.CompareSimilarity(sentence_copy, example_sentence) #We use the Spacy similarity feature to go more in depth into the analysis
                        if(score >= 0.9 and score < 0.93):
                            sentence_status=2
                        elif(score >=0.93):
                            sentence_status=3
                if sentence_status>0:
                    self.crit_sents.append(sentence) #We save the sentence as critical
                    self.crit_sents.append("("+str(sentence_status)+")")
                if sentence_status>self.status:
                    if sentence_status==1:
                        self.status=1
                        self.result="/!\\ A level 1 alert has been raised /!\\"
                    elif sentence_status==2:
                        self.status=2
                        self.result="/!\\ A level 2 alert has been raised /!\\"
                    elif sentence_status==3:
                        self.status=3
                        self.result="/!\\ A level 3 alert has been raised /!\\"


    def RunAnalysis(self, wordDic=[], sentDic=[]):
        if wordDic==[]: 
            wordDic=TextAnalyzer.wordDic
        if sentDic==[]:
            sentDic=TextAnalyzer.LoadSentenceDic("analyzer_tools/Sentence_dictionnary.txt", self.company)
        self.date=datetime.now()
        self.status=0 #Default status
        self.result="Nothing to report." #Default result
        sentence_status=0
        compsentences=TextAnalysis.DetectSentences(self.text, [self.company]) #First, we start by extracting the sentences where the company is mentionned.
        for sentence in compsentences:
            sentence_copy=str(sentence).lower() #To simplify the comparison process, all compared sentences will be in lowercase.
            date_too_old=False #We then check whether the sentence mentions an event that has occured more than a week prior to the article/tweet date.
            DetectedDates=TextAnalysis.IdentifyDateSentence(sentence_copy, datetime.combine(self.text_date, datetime.min.time()))
            for date in DetectedDates:
                if date < self.text_date-timedelta(days=7):
                    date_too_old=True
            if date_too_old==False:
                #----------------------------First layer of analysis-----------------------------------------
                for word in wordDic: #We now browse our word Dictionnary
                    if word in sentence_copy: #To check if the sentence also countains one of these words.
                        sentence_status=1
                        break #We do not need to check whether the sentence contains other words from the dictionnary as we will not save it more than once.
                #----------------------------Second layer of analysis-----------------------------------------
                if sentence_status==1:
                    try:
                        subj=TextAnalysis.IdentifySubject(sentence_copy) #The main subject of the sentence
                        root=TextAnalysis.IdentifyRoot(sentence_copy) #The root of the sentence
                        if subj[0] in wordDic or TextAnalysis.GetLemma(subj[0]) in wordDic:
                            sentence_status=2
                        if root[0] in wordDic or TextAnalysis.GetLemma(root[0]) in wordDic:
                            sentence_status=2
                    except:
                        pass
                #----------------------------Third layer of analysis-----------------------------------------
                if sentence_status==2:
                    for example_sentence in sentDic:
                        score=TextAnalysis.CompareSimilarity(sentence_copy, example_sentence) #We use the Spacy similarity feature to go more in depth into the analysis
                        if(score >= 0.93):
                                sentence_status=3
                if sentence_status>0:
                    self.crit_sents.append(sentence) #We save the sentence as critical
                    self.crit_sents.append("("+str(sentence_status)+")")
                if sentence_status>self.status:
                    if sentence_status==1:
                        self.status=1
                        self.result="/!\\ A level 1 alert has been raised /!\\"
                    elif sentence_status==2:
                        self.status=2
                        self.result="/!\\ A level 2 alert has been raised /!\\"
                    elif sentence_status==3:
                        self.status=3
                        self.result="/!\\ A level 3 alert has been raised /!\\"

    
    def Save(self):
        if self.status>0:
            path="analysis_results/{}".format(date.today())
            if not os.path.exists(path):
                os.mkdir(path)
            path+="/"+self.company
            if not os.path.exists(path):
                os.mkdir(path)
            with open (path+"/{}".format(str(self.Id)+"-"+str(self.status)+".txt"), "w", encoding="utf-8") as file: 
                file.write(self.__str__())

    if __name__=="__main__":
        #Test()
        print("")


