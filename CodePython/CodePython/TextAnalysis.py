#Objectif : trier les données des textes après scraping pour ensuite identifier une éventuelle menace/attaque visant une des entreprises partenaire

import numpy as np
import spacy
import pickle
import requests
from bs4 import BeautifulSoup
from dateparser import parse 
from dateparser.search import search_dates
import datetime
import time
import re
from nltk import word_tokenize, pos_tag
#python -m spacy download en_core_web_md
nlp = spacy.load('en_core_web_md')
import warnings
warnings.filterwarnings("ignore", message="The localize method is no longer necessary, as this time zone supports the fold attribute")
#https://spacy.io/usage/linguistic-features | https://spacy.io/api/token#attributes | https://spacy.io/api/token

def extract_example(number): #Don't forget to update the number
    """
    Extracts an article from a webpage and saves it to a txt file.

    Parameter
    -------------
    number: int
        The article number in our folder containing all the txt files.
    """
    URL="https://www.zdnet.com/article/sec-filings-solarwinds-says-18000-customers-are-impacted-by-recent-hack/" #changer l'url
    page=requests.get(URL)
    soup=BeautifulSoup(page.text, "lxml")

    example_bloc=""
    for paragraph in soup.find_all('p'):
        example_bloc+=(paragraph.text)+"\n"
    example_bloc+="\n\n"+URL

    with open("articles/article{}.txt".format(str(number)), "w") as file:
        file.write(example_bloc)
    file.close()

def LoadExampleText(number):
    """
    Reads a txt article file to return the corresponding str object.

    Parameter
    -------------
    number: int
        The article number in our folder containing all the txt files.
    """
    with open("articles/article{}.txt".format(str(number)), "r") as file: #changer le numéro de l'article
        text=file.read()
    file.close()
    return text

#For testing purposes
example_bloc=LoadExampleText(1)
keywords=["vulnerability", "attack", "threat", "breach"]


def CountOccurences(keywords, text):
    """
    Counts how many times the text mentions a keyword in the given list

    Parameters:
    -------------
    keywords: list
        keywords to count
    text: str
        analyzed text
    """
    occurence = 0

    doc = nlp(text) #We create a spacy nlp object

    for token in doc: #We loop through each token (a toekn is either a word or ponctuation)
        if keywords and len(keywords) != 0:
            for k in keywords:
                if(token.text == k):
                    occurence += 1
    return occurence

#For testing purposes
def TestCountOccurences():
    keywords = ['breach']
    with open('article.txt', 'r') as f:
        text = f.read() 
    occ = CountOccurences(keywords, text)
    print(occ)

#For testing purposes
def TestCountOccurences(text):
    keywords = ['security']
    occ = CountOccurences(keywords, text)
    print(occ)

def IdentifySubject(sentence):
    """
    Returns a tuple of size 2 containing the text of the subject and its spacy dependency.

    Parameters:
    -------------
    sentence: str
        analyzed sentence
    """
    doc = nlp(sentence)
    for token in doc:
        if token.dep_ == "nsubj" or token.dep_== "nsubjpass":
            return token.text, token.dep_

#For testing purposes
def TestIdentifySubject(text):
    doc = nlp(text)
    first_sentence = list(doc.sents)[0].text
    print("Test sentence : " + first_sentence)
    subject = IdentifySubject(first_sentence)
    print("Subject : " + subject)

def DetectSentences(text, keywords):
    """
    Returns the sentences that contain at least one keyword

    Parameters:
    -------------
    keywords: list
        list of keywords we want to detect
    text: str
        analyzed text
    """
    doc=nlp(text)
    keysentences=[]

    for sentence in list(doc.sents):
        sentence_copy=str(sentence).lower()
        for keyword in keywords:
            if keyword.lower() in sentence_copy:
                keysentences.append(sentence)
                break #Pour ne pas prendre plusieurs fois la même phrase si elle contient plusieurs des mots présents dans la liste
    return keysentences

#For testing purposes
def TestDetectSentences(text):
    sentences=DetectSentences(text, keywords)
    print(sentences)

def ConversionDateArticle(date):
    """
    Converts an object datetime in a list [day, month, year]

    Parameters:
    -------------
    date: date
        date to convert
    """
    day= date.apply(lambda x : datetime.strptime(x,'%d/%m/%Y').weekday())
    month= date.apply(lambda x : datetime.strptime(x,'%d/%m/%Y').month)
    year= date.apply(lambda x : datetime.strptime(x,'%d/%m/%Y').year)

    tab=[day,month,year]
    return tab

def DetectDateOfAttack (date,sentence):
    mois=[1,2,3,4,5,6,7,8,9,10,11,12]
    timeWords={"yesterday":1, "today":0}
    #date=ConversionDateArticle(dateArticle)
    for cle,valeur in timeWords.items():
        if cle in sentence:
            date[0]=date[0]-valeur
    
    day=re.search("\d{1,3}.day.*ago",sentence)
    if day :
        day=re.search("\d{1,3}",day.group())
        date[0]=date[0]-int(day.group())
        
    month=re.search("\d{1,3}.month.*ago",sentence)
    if month :
        month=re.search("\d{1,3}",month.group())
        
        for i in range(len(mois)):
            if date[1]==mois[i]:
                index=i-int(month.group())
                date[1]=mois[index]
                break
        
        #date[1]=date[1]-int(month.group())
    
    year=re.search("\d{1,5}.year.*ago",sentence)
    if year :
        year=re.search("\d{1,5}",year.group())
        date[2]=date[2]-int(year.group())
    
    return date

#Identifier une date dans une phrase et la retourne en un objet de type datetime
#pip install dateparser

#Pour supprimer les warnings du package dateparser


def IdentifyDateSentence(sentence, relativeDate):
    """
    Identifies one of multiple dates in a sentence and returns it in a list of datetime objects

    Parameters:
    -------------
    sentence: str
        analyzed sentence
    relativeDate: datetime
        date of the article
    """
    extractedDates = search_dates(sentence, languages = ['en'], settings={'RELATIVE_BASE' : relativeDate}) #array containing the dates extracted from the given sentence
    tableauDates = [] #array containing these dates as datetime objects
    if extractedDates is not None:
        for i in range(len(extractedDates)):
            tableauDates.append(extractedDates[i][1].date())
    return tableauDates

def IdentifyDateInText(text, relativeDate):
    """
    Identifies one of multiple dates in a text and prints it

    Parameters:
    -------------
    text: str
        analyzed text
    relativeDate: datetime
        date of the article
    """
    doc = nlp(text)
    for sentence in list(doc.sents):
        if(sentence is not None):
            print("---------------Phrase---------------\n" + sentence.text)
            text = sentence.text
            dates = IdentifyDateSentence(text, relativeDate)
            if len(dates) != 0:
                print("Dates identifiées : ")
                for date in dates:
                    print(date)
            else:
                print("Aucune date trouvée.")
            print("\n")

def TestIdentifyDateInText():
    with open('article.txt', 'r') as f:
        text = f.read()
    #text = LoadExampleText()
    relativeDate = datetime.datetime(2021, 1, 2)
    IdentifyDateInText(text, relativeDate)


def LexicalField(keyword):
    """
    List words of the lexical field of a keyword

    Parameters:
    -------------
    keyword: str
    """
    #This function finds the most similar words and places them in an array (called ms here).
    ms = nlp.vocab.vectors.most_similar(np.asarray([nlp.vocab.vectors[nlp.vocab.strings[keyword]]]), n=10)
    for word in ms[0][0]:
        keyword = nlp.vocab.strings[word]
        print(keyword)
        #We ask the admin whether they want to add this word in our keyword list or not.
        add = input("Add '" + keyword + "' to the list of keyword ? (y/n) : ") 
        while(add != 'y' and add != 'n'):
            add = input("Incorrect entry. \nAdd '" + keyword + "' to the list of keyword ? (y/n) : ") 
        if(add == 'y'):
            keywords.append(keyword) #We add the word approved by the admin.

def TestLexicalField():
    keyword = 'cyberattack'
    LexicalField(keyword)
    print(keywords)

def CompareSimilarity(text1, text2):
    """
    Compares the similarity between 2 texts and returns a similarity coefficient between 0 to 1 (0 being no similarity and 1 being identical)

    Parameters:
    -------------
    text1: str
        First text to be compared
    text2: str
        Second text to be compared
    """
    doc1 = nlp(text1)
    doc2 = nlp(text2)
    sim=doc1.similarity(doc2)
    return sim

def GetLemma(word):
    doc=nlp(word)
    return doc[0].lemma_

def DetectTenses(sentence):
    """
    Detects tenses of the verbs in a sentence and returns it in a dictionary

    Parameters:
    -------------
    sentence: str
    """
    tenses = []
    text = word_tokenize(sentence)
    #pos_tag reurns a list of tuples under the form [(mot1, tag1), (mot2, tag2), ... ]
    words = pos_tag(text)
    print(words)
    for i in range(len(words)):
        #PAST TENSE
        #If the verb is in preterite
        if words[i][1] == 'VBD': 
            if words[i][0] == 'had':
                #If it is followed by a past participle,
                if words[i+1][1] == 'VBN':
                    tenses.append((str(words[i][0]) + ' ' + str(words[i+1][0]), 'pluperfect -> distant past'))
                    i += 1
                #If there is an adverb between the modal and the past participle
                elif words[i+2][1] == 'VBN':
                    tenses.append((str(words[i][0]) + ' ' + str(words[i+2][0]), 'pluperfect -> distant past'))
                    i += 2
            #If it is a preterite verb
            else:
                tenses.append((words[i][0], 'preterit'))
        
        #PRESENT TENSE
        #If the verb is in the present tense
        elif words[i][1] in ['VBP', 'VBZ']:
            if words[i][0] in ['has', 'have']:
                #If it is followed by a past participle
                if words[i+1][1] == 'VBN':
                    tenses.append((str(words[i][0]) + ' ' + str(words[i+1][0]), 'present perfect'))
                    i += 1
                #If there is an adverb between the modal and the past participle
                elif words[i+2][1] == 'VBN':
                    tenses.append((str(words[i][0]) + ' ' + str(words[i+2][0]), 'present perfect'))
                    i += 2
                else:
                    tenses.append((words[i][0], 'present'))
            #If followed by a verb in -ing
            elif(words[i+1][1] == 'VBG'):
                tenses.append((str(words[i][0]) + ' ' + str(words[i+1][0]), 'present continuous'))
                i += 1
            elif(words[i+2][1] == 'VBG'):
                tenses.append((str(words[i][0]) + ' ' + str(words[i+2][0]), 'present continuous'))
                i += 2
            else:
                tenses.append((words[i][0], 'present'))

        #If the verb is a modal
        elif(words[i][1] == 'MD'):
            #FUTUR TENSE
            if(words[i][0] == 'will'):
                if(words[i+1][0] == 'have' and words[i+2][1] == 'VBN'):
                    tenses.append((str(words[i][0]) + ' ' + str(words[i+1][0]) + ' ' + str(words[i+2][0]), 'futur antérieur'))
                    i += 2
                elif(words[i+2][0] == 'have' and words[i+3][1] == 'VBN'):
                    tenses.append((str(words[i][0]) + ' ' + str(words[i+2][0]) + ' ' + str(words[i+3][0]), 'futur antérieur'))
                    i += 3
                else:
                    tenses.append((str(words[i][0]) + ' ' + str(words[i+1][0]), 'future'))
    return tenses

def IdentifyRoot(sentence):
    """
    Returns a tuple of size 2 containing the text of the root and its spacy dependency.

    Parameters:
    -------------
    sentence: str
        analyzed sentence
    """
    root=""
    doc=nlp(sentence)
    for token in doc:
        if token.dep_=="ROOT":
            return token.text, token.dep_

def detailSpacy(sentence):
    """
    Displays all variables for each token object in a given sentence.

    Parameters:
    -------------
    sentence: str
        The sentence from which we will extract the tokens.
    """
    doc=nlp(sentence)
    for token in doc:
        print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_,token.shape_, token.is_alpha, token.is_stop)


def TestDetectTenses():
    sentence = "Cisco will just have been making it in an advisory published this week."
    tenses = DetectTenses(sentence)
    print('\n------------------------------Detected verbs------------------------------')
    print(tenses)

def SyntacticTests():
    sentence="SolarWinds disclosed on Sunday that a nation-state hacker group breached its network and inserted malware in updates for Orion, a software application for IT inventory management and monitoring."
    doc=nlp(sentence)
    ancestors_list=[]
    conjuncts_list=[]
    children_list=[]
    for a in doc[10].ancestors:
        ancestors_list.append(a)
    print(ancestors_list)
    for c in doc[10].conjuncts:
        conjuncts_list.append(c)
    print(conjuncts_list)
    for child in doc[10].children:
        children_list.append(child)
    print(children_list)

def main_function():
    #print(example_bloc)
    #TestDetectSentences(example_bloc)
    #TestCompteurOccurences()
    #TestIdentifierSujet()
    #TestIdentifyDateInText()
    #TestLexicalField()
    #TestDetectTenses()
    #extract_example(10)
    detailSpacy("SolarWinds disclosed on Sunday that a nation-state hacker group breached its network and inserted malware in updates for Orion, a software application for IT inventory management and monitoring.")
    SyntacticTests()

if __name__=="__main__":
    main_function()


