#Objectif : trier les données des textes après scraping pour ensuite identifier une éventuelle menace/attaque visant une des entreprises partenaire

import numpy as np
import spacy
import pickle
import requests
from bs4 import BeautifulSoup
from dateparser import parse 
from dateparser.search import search_dates
import datetime
#python -m spacy download en_core_web_sm
nlp = spacy.load('en_core_web_sm')

#Pour extraire un article depuis une page web qui servira ensuite d'exemple pour toutes nos fonctions de test.
#On extraie un article que l'on sauvegarde ensuite dans un objet string puis dans un fichier pickle.
def extract_example():
    URL="https://thehackernews.com/2022/01/cisco-releases-patch-for-critical-bug.html"
    page=requests.get(URL)
    soup=BeautifulSoup(page.text, "lxml")

    example_bloc=""
    for paragraph in soup.find_all('p'):
        example_bloc+=(paragraph.text)+"\n"

    with open("paragraphex.pickle", "wb") as file:
        pickle.dump(example_bloc, file)
    file.close()

def LoadExampleText():
    with open("paragraphex.pickle", "rb") as file:
        text=pickle.load(file)
    file.close()
    return text

#Pour effectuer des tests, nous utiliserons un paragraphe à titre d'exemple.
example_bloc=LoadExampleText()
#Cisco Systems has rolled out security updates for a critical security vulnerability affecting Unified Contact Center Management Portal (Unified CCMP) and Unified Contact Center Domain Manager (Unified CCDM) that could be exploited by a remote attacker to take control of an affected system.
#Tracked as CVE-2022-20658, the vulnerability has been rated 9.6 in severity on the CVSS scoring system, and concerns a privilege escalation flaw arising out of a lack of server-side validation of user permissions that could be weaponized to create rogue Administrator accounts by submitting a crafted HTTP request.
#"With these accounts, the attacker could access and modify telephony and user resources across all the Unified platforms that are associated to the vulnerable Cisco Unified CCMP," Cisco noted in an advisory published this week. " To successfully exploit this vulnerability, an attacker would need valid Advanced User credentials."
#Unified CCMP and Unified CCDM product versions 12.5.1, 12.0.1, and 11.6.1 and earlier running with default configuration are impacted, the networking equipment company said, adding it found the issue as part of a Technical Assistance Center (TAC) support case. Version 12.6.1 of the software is not affected.
#While there is no evidence that the security flaw has been exploited in real-world attacks, it's recommended that users upgrade to the latest version to mitigate the risk associated with the flaws.
#Sign up for cybersecurity newsletter and get latest news updates delivered straight to your inbox daily.

example_sentence=("Cisco Systems has rolled out security updates for a critical security vulnerability affecting Unified Contact Center" 
" Management Portal (Unified CCMP) and Unified Contact Center Domain Manager (Unified CCDM) that could be exploited by a remote attacker to take control of an affected system.")

#Les mots clés que l'on utilisera pour trouver/cibler certaines phrases de notre texte, 
keywords=["vulnerability", "attack", "threat", "breach"]


#Retourne le nombre de fois qu'un mot clé ait apparu dans le texte
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

#Identifier une date dans une phrase et la retourne en un objet de type datetime
#pip install dateparser

#Pour supprimer les warnings du package dateparser
import warnings
warnings.filterwarnings("ignore", message="The localize method is no longer necessary, as this time zone supports the fold attribute")

def IdentifyDate(sentence, relativeDate):

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
            dates = IdentifyDate(text, relativeDate)
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
        add = input("Add to the list of keyword ? (y/n) : ") 
        if(add == 'y'):
            keywords.append(keyword)
    #Puis les ajouter à la liste de mots-clés

def TestLexicalField():
    keyword = 'cyberattack'
    LexicalField(keyword)
    print(keywords)


def main():
    #print(example_bloc)
    #TestDetectSentences(example_bloc)
    #TestCompteurOccurences()
    #TestIdentifierSujet()
    #TestIdentifyDateInText()
    TestLexicalField()

main()


##Tester la similarité de deux phrases
#doc1 = nlp("PNB customers' data exposed for seven months du to server vulnerability")
#doc2 = nlp("Polish T-Mobile unit faces cyber attack, systems not compromised ")
#print(doc1, '<->', doc2, doc1.similarity(doc2))
#doc3 = nlp("5 Simple steps to protect your practice from cyberattacks")
#print(doc2, '<->', doc3, doc2.similarity(doc3))
##Résultats : 0.7528227008873364 et 0.7557642629789989, il montre les similarités dans le vocabulaire mais ne différencie pas le contexte