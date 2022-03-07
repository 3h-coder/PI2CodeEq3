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
                    line=line.replace("CompName", company)
                SentDic.append(line.rstrip())
        return SentDic

    #Class attributes
    Id=0
    wordDic=LoadWordDic("analyzer_tools/Keyword_dictionnary.txt")

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
        max_rate=0.92 #If this similarity score is reached or exceeded, a level 3 alert is raised.
        med_rate=0.8
        lvl2_rate_nb=20 #If 10 scores are located between the med_rate and max_rate, a level 2 alert is raised.
        lvl1_rate_nb=15 #If 5 scores are located between the med_rate and max_rate, a level 1 alert is raised.
        self.date=datetime.now()
        self.status=0 #Default status
        self.result="Nothing to report." #Default result
        similarityScores={}
        keysentences=TextAnalysis.DetectSentences(self.text, wordDic) #First, we start by extracting the sentences that contain our keywords.
        for text_sentence in keysentences: #Then, we compare each of these sentences with the example phrases from our sentDic variable.
            text_sentence_copy=str(text_sentence).lower() #To simplify the comparison process, all compared sentences will be in lowercase.
            DetectedDates=TextAnalysis.IdentifyDateSentence(str(text_sentence), datetime.combine(self.text_date, datetime.min.time())) #We now want to make sure that the sentence doesn't mention 
            #an event that is too old and thus irrelevant. (We want to avoid false positives by doing that)
            for date in DetectedDates:
                if date < self.text_date-timedelta(days=7): #If the occurence happened more than a week before the article/tweet post date, it is considered as too old.
                    try:
                        keysentences.remove(text_sentence) #We remove the sentence from our list.
                    except:
                        pass
            similarityScores[text_sentence]=[]
            for example_sentence in sentDic:
                score=TextAnalysis.CompareSimilarity(text_sentence_copy,str(example_sentence)) #We evaluate the similarity between the extracted sentence and the example sentence lowercased.
                #if score > 0.9:
                    #print("There is a very high similarity between our text sentence:\""+str(text_sentence)+"\" and our example sentence:\"" \
                        #+str(example_sentence)+"\" (score of:"+str(score)+")")
                #elif score > 0.8:
                    #print("There is medium similarity between our text sentence:\""+str(text_sentence)+"\" and our example sentence:\"" \
                        #+str(example_sentence)+"\" (score of:"+str(score)+")")
                #else:
                    #print("There is a low similarity between our text sentence:\""+str(text_sentence)+"\" and our example sentence:\"" \
                        #+str(example_sentence)+"\" (score of:"+str(score)+")")    
                similarityScores[text_sentence].append(score) #And save the score
                #print("----------------------------------next example sentence----------------------------------")
            #print("----------------------------------||next text sentence||----------------------------------")
        for key in similarityScores: #We then browse for each extracted sentence the corresponding scores. Key is the extracted sentence, value is the list of scores after comparison (len(value)==len(sentDic)).
            scores=similarityScores[key]
            count_med_rate=0
            for score in scores: #We browse the score list for a given sentence.
                if score>=max_rate:  #We verify whether the maximum score is reached or exceeded, if so we raise a level 3 alert. 
                    self.status=3
                    self.result="/!\\ A level 3 alert has been raised /!\\"
                    break #We move on to the next phrase as it will never be higher.
                if score>med_rate and score<max_rate:
                    count_med_rate+=1
                    if count_med_rate >= lvl2_rate_nb:
                        if self.status < 3: #A lower status cannot overwrite a higher one.
                            self.status=2
                            self.result="/!\\ A level 2 alert has been raised /!\\"
                            #We do not move on to the next phrase here because there is a possibility that the next score will be > max_rate 
                            #and thus overwrite this assignment.
                    if count_med_rate >= lvl1_rate_nb:
                        if self.status < 2:
                            self.status=1
                            self.result="/!\\ A level 1 alert has been raised /!\\"
                            #We do not move on to the next phrase here because there is a possibility that the next score is > max_rate or that
                            #count_med_rate will become >= lvl2_rate_nb and thus overwrite this assignment.
            if self.status>0: #If the sentence raised an alert, we save it in our crit_sents variable.
                self.crit_sents.append(key)
        #print("Number of critical sentences :"+str(len(self.crit_sents)))

    def RunAnalysis(self, wordDic=[]):
        if wordDic==[]: 
            wordDic=TextAnalyzer.wordDic
        count=0 #The number of critical sentences
        self.date=datetime.now()
        self.status=0 #Default status
        self.result="Nothing to report." #Default result
        compsentences=TextAnalysis.DetectSentences(self.text, [self.company])
        for sentence in compsentences:
            date_too_old=False
            DetectedDates=TextAnalysis.IdentifyDateSentence(str(sentence), datetime.combine(self.text_date, datetime.min.time())) #We now want to make sure that the sentence doesn't mention 
            #an event that is too old and thus irrelevant. (We want to avoid false positives by doing that)
            for date in DetectedDates:
                if date < self.text_date-timedelta(days=7): #If the occurence happened more than a week before the article/tweet post date, it is considered as too old.
                    date_too_old=True
            if not date_too_old:
                sentence_copy=str(sentence).lower()
                for word in wordDic:
                    if word in sentence_copy:
                        count+=1
                        self.crit_sents.append(sentence)
                        break
        if count >= 5:
            self.status=3
            self.result="/!\\ A level 3 alert has been raised /!\\"
        elif count >=3:
            self.status=2
            self.result="/!\\ A level 2 alert has been raised /!\\"
        elif count >=1:
            self.status=1
            self.result="/!\\ A level 1 alert has been raised /!\\"


    def Save(self):
        path="analysis_results/{}".format(date.today())
        if not os.path.exists(path):
            os.mkdir(path)

        with open (path+"/{}".format(self.company+"-"+str(self.Id)+"-"+str(self.status)+".txt"), "w", encoding="utf-8") as file: 
            file.write(self.__str__())

    if __name__=="__main__":
        #Test()
        print("")


