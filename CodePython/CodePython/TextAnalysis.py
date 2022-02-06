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

#Pour extraire un article depuis une page web qui servira ensuite d'exemple pour toutes nos fonctions de test.
def extract_example(number): #bien mettre à jour le numéro
    URL="https://krebsonsecurity.com/2022/01/500m-avira-antivirus-users-introduced-to-cryptomining/" #changer l'url
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
    with open("articles/article{}.txt".format(str(number)), "r") as file: #changer le numéro de l'article
        text=file.read()
    file.close()
    return text

#Pour effectuer des tests, nous utiliserons un paragraphe à titre d'exemple.
#extract_example(1)
example_bloc=LoadExampleText(1)

#Les mots clés que l'on utilisera pour trouver/cibler certaines phrases de notre texte, 
keywords=["vulnerability", "attack", "threat", "breach"]


#Retourne le nombre de fois qu'un mot clé est apparu dans le texte
def CountOccurences(keywords, text):
    occurence = 0

    doc = nlp(text) #On crée un objet spacy appelé doc qui contient le texte passé en paramètre

    for token in doc: #Boucle sur chaque token (un token est un mot ou une ponctuation)
        if keywords and len(keywords) != 0:
            for k in keywords:
                if(token.text == k):
                    occurence += 1
    return occurence

#Test de la fonction Compte Occurences KeyWord
def TestCountOccurences():
    keywords = ['breach']
    with open('article.txt', 'r') as f:
        text = f.read() 
    occ = CountOccurences(keywords, text)
    print(occ)

#Test de la fonction CountOccurences
def TestCountOccurences(text):
    keywords = ['security']
    occ = CountOccurences(keywords, text)
    print(occ)

#Retourne un string qui est le sujet de la phrase passée en paramètre
def IdentifySubject(sentence):
    doc = nlp(sentence)
    for token in doc:
        if token.dep_ == 'nsubj':
            return token.text

#Test de la fonction IdentifySubject
def TestIdentifySubject(text):
    doc = nlp(text)
    first_sentence = list(doc.sents)[0].text
    print("Test sentence : " + first_sentence)
    subject = IdentifySubject(first_sentence)
    print("Subject : " + subject)

#Pour identifier les phrases contenant une liste de mots spécifiés
def DetectSentences(text, keywords):
    doc=nlp(text)
    keysentences={}
    count=0

    for sentence in list(doc.sents):
        for keyword in keywords:
            if keyword in str(sentence):
                count+=1
                keysentences[count]=sentence
                break #Pour ne pas prendre plusieurs fois la même phrase si elle contient plusieurs des mots présents dans la liste

    return keysentences

#Test de la fonction DetectSentences 
def TestDetectSentences(text):
    sentences=DetectSentences(text, keywords)
    print(sentences)

#Pour déterminer le temps de la phrase (passé, présent ou futur). /!\ En anglais!
def DetectTense(sentence):
    tense=""
    return tense

def ConversionDateArticle(date):
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
import warnings
warnings.filterwarnings("ignore", message="The localize method is no longer necessary, as this time zone supports the fold attribute")

def IdentifyDateSentence(sentence, relativeDate):

    #La méthode search_dates renvoie une liste de tuples
    #Chaque tuple correspond à (date ou expression temporelle repérée dans un string, objet datetime correspondant)
    extractedDates = search_dates(sentence, languages = ['en'], settings={'RELATIVE_BASE' : relativeDate}) #Tableau contenant les dates repérées dans la phrase passée ne paramètre
    tableauDates = [] #Tableau des dates extraites sous forme d'objet datetime
    if extractedDates is not None:
        for i in range(len(extractedDates)):
            tableauDates.append(extractedDates[i][1])
    return tableauDates

def IdentifyDateInText(text, relativeDate):
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


#Pour trouver les mots similaires au mot cyberattack et les placer dans la liste keywords
def LexicalField(keyword):
    #Cette fonction spacy trouve les mots les plus similaires et les place dans un array appelé ici ms
    ms = nlp.vocab.vectors.most_similar(np.asarray([nlp.vocab.vectors[nlp.vocab.strings[keyword]]]), n=10)
    for word in ms[0][0]:
        keyword = nlp.vocab.strings[word]
        print(keyword)
        #On demande à l'admin s'il veut rajouter ce mot à la liste de mots clés
        add = input("Add '" + keyword + "' to the list of keyword ? (y/n) : ") 
        while(add != 'y' and add != 'n'):
            add = input("Incorrect entry. \nAdd '" + keyword + "' to the list of keyword ? (y/n) : ") 
        if(add == 'y'):
            keywords.append(keyword) #On ajoute le mot clé validé par l'admin

def TestLexicalField():
    keyword = 'cyberattack'
    LexicalField(keyword)
    print(keywords)

#A faire la première fois que vous lancez le code:
#import nltk
#nltk.download('punkt')
#nltk.download('averaged_perceptron_tagger')
#nltk.download('universal_tagset')


#Pour déterminer le temps de la phrase (passé, présent ou futur). /!\ En anglais!
def DetectTenses(sentence):
    tenses = []
    text = word_tokenize(sentence)
    #pos_tag renvoie une liste de tuples sous la forme [(mot1, tag1), (mot2, tag2), ... ]
    words = pos_tag(text)
    print(words)
    for i in range(len(words)):
        #TEMPS DU PASSE
        #Si le verbe est au preterit 
        if words[i][1] == 'VBD': 
            if words[i][0] == 'had':
                #S'il est suivi par un participe passé,
                if words[i+1][1] == 'VBN':
                    tenses.append((str(words[i][0]) + ' ' + str(words[i+1][0]), 'pluperfect -> distant past'))
                    i += 1
                #S'il y a un adverbe entre le modal et le participe passé
                elif words[i+2][1] == 'VBN':
                    tenses.append((str(words[i][0]) + ' ' + str(words[i+2][0]), 'pluperfect -> distant past'))
                    i += 2
            #Si c'est un verbe au preterit
            else:
                tenses.append((words[i][0], 'preterit'))
        
        #TEMPS DU PRESENT
        #Si le verbe est au présent
        elif words[i][1] in ['VBP', 'VBZ']:
            if words[i][0] in ['has', 'have']:
                #S'il est suivi d'un participe passé
                if words[i+1][1] == 'VBN':
                    tenses.append((str(words[i][0]) + ' ' + str(words[i+1][0]), 'present perfect'))
                    i += 1
                #S'il y a un adverbe entre le modal et le participe passé
                elif words[i+2][1] == 'VBN':
                    tenses.append((str(words[i][0]) + ' ' + str(words[i+2][0]), 'present perfect'))
                    i += 2
                else:
                    tenses.append((words[i][0], 'present'))
            #S'il est suivi par un verbe en -ing
            elif(words[i+1][1] == 'VBG'):
                tenses.append((str(words[i][0]) + ' ' + str(words[i+1][0]), 'present continuous'))
                i += 1
            elif(words[i+2][1] == 'VBG'):
                tenses.append((str(words[i][0]) + ' ' + str(words[i+2][0]), 'present continuous'))
                i += 2
            else:
                tenses.append((words[i][0], 'present'))

        #Si le verbe est un modal
        elif(words[i][1] == 'MD'):
            #TEMPS DU FUTUR
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

def TestDetectTenses():
    sentence = "Cisco will just have been making it in an advisory published this week."
    tenses = DetectTenses(sentence)
    print('\n------------------------------Verbes détectés------------------------------')
    print(tenses)

def main_function():
    #print(example_bloc)
    #TestDetectSentences(example_bloc)
    #TestCompteurOccurences()
    #TestIdentifierSujet()
    #TestIdentifyDateInText()
    #TestLexicalField()
    TestDetectTenses()
    #extract_example()

if __name__=="__main__":
    main_function()


##Tester la similarité de deux phrases
#doc1 = nlp("PNB customers' data exposed for seven months du to server vulnerability")
#doc2 = nlp("Polish T-Mobile unit faces cyber attack, systems not compromised ")
#print(doc1, '<->', doc2, doc1.similarity(doc2))
#doc3 = nlp("5 Simple steps to protect your practice from cyberattacks")
#print(doc2, '<->', doc3, doc2.similarity(doc3))
##Résultats : 0.7528227008873364 et 0.7557642629789989, il montre les similarités dans le vocabulaire mais ne différencie pas le contexte
