#Objectif : trier les données des textes après scraping pour ensuite identifier une éventuelle menace/attaque visant une des entreprises partenaire


import pandas
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
stemmer = SnowballStemmer(language='english')
#CMD
#pip install nltk

#Python console
#import nltk
#nltk.download('stopwords')


from dateparser import parse 
from dateparser.search import search_dates
import numpy as np
import spacy
#python -m spacy download en_core_web_md
#nlp = spacy.load('en_core_web_md')


#python -m spacy download en_core_web_lg
nlp = spacy.load('en_core_web_lg')




#Retourne le nombre de fois qu'un mot clé ait apparu dans le texte
def CompteurOccurences(keywords, text):
    print('\n-------------------Identifier des mots clés dans les textes à analyser----------------------------\n')

    occurence = 0

    doc = nlp(text) #On crée un objet spacy appelé doc qui contient le texte passé en paramètre

    for token in doc: #Boucle sur chaque token (un token est un mot ou une ponctuation)
        if keywords and len(keywords) != 0:
            for k in keywords:
                if(token.text == k):
                    occurence += 1
    return occurence

#Test de la fonction CompteOccurencesKeyWord
def TestCompteurOccurences():
    keywords = ['breach']
    with open('article.txt', 'r') as f:
        text = f.read() 
    occ = CompteurOccurences(keywords, text)
    print(occ)

#Test de la fonction CompteOccurencesKeyWord
def TestCompteurOccurences():
    keywords = ['breach']
    with open('article.txt', 'r') as f:
        text = f.read() 
    occ = CompteurOccurences(keywords, text)
    print(occ)


#Retourne un string qui est le sujet de la phrase passée en paramètre
def IdentifierSujet(sentence):
    doc = nlp(sentence)
    for token in doc:
        if token.dep_ == 'nsubj':
            return token.text

#Test de la fonction IdentifierSujet
def TestIdentifierSujet():
    with open('article.txt', 'r') as f:
        text = f.read()
    doc = nlp(text)
    print("Phrase test : " + list(doc.sents)[0].text)
    sentence = list(doc.sents)[0].text
    sujet = IdentifierSujet(sentence)
    print("Sujet : " + sujet)

#Identifier une date dans une phrase et la retourne en un objet de type datetime
#pip install dateparser

#Pour supprimer les warnings du package dateparser
import warnings
warnings.filterwarnings("ignore", message="The localize method is no longer necessary, as this time zone supports the fold attribute")

def IdentifierDate(sentence):
    #La méthode search_dates renvoie une liste de tuples
    #Chaque tuple correspond à (date ou expression temporelle repérée dans un string, objet datetime correspondant)
    extractedDates = search_dates(sentence, languages = ['en']) #Tableau contenant les dates repérées dans la phrase passée ne paramètre
    tableauDates = [] #Tableau des dates extraites sous forme d'objet datetime
    if extractedDates is not None:
        for i in range(len(extractedDates)):
            tableauDates.append(extractedDates[i][1])
            print(extractedDates[i])
    return tableauDates

def TestIdentifierDate():
    with open('article.txt', 'r') as f:
        text = f.read()
    doc = nlp(text)
    for sentence in list(doc.sents):
        if(sentence is not None):
            print("---------------Phrase---------------\n" + sentence.text)
            text = sentence.text
            dates = IdentifierDate(text)
            if len(dates) != 0:
                print("Dates identifiées : ")
                for date in dates:
                    print(date)
            else:
                print("Aucune date trouvée.")
            print("\n")

def GenerateRelevant(CompanyName):
    Comparison_Relevant=["The company "+CompanyName+" is attacked by pirates","company "+CompanyName+" suffers from cyberattackers","A security breach was detected"]


def seperateBySentence(stringarray,CompanyName):
    count=1
    Comparison_Relevant=["The company is attacked by pirates","The company suffers from cyberattackers","A security breach was detected"]
    for string in stringarray:
        print("Paragraphe "+str(count))
        if(string==""):
            print("paragraphe vide")
        else:
            # Tokeniser le string
            doc = nlp(string)
            # Séparer le string en plusieurs phrases
            sentences=[X.text for X in doc.sents]
            print("sentences")
            for sentence in sentences:
                print("-----------------New sentence----------------")
                print(sentence)
                print("sujet de la phrase")
                print(IdentifierSujet(sentence))
                print("dates dans la phrase")
                IdentifierDate(sentence)
                print("tokens")
                extractTokens(sentence)
                doc_sentence = nlp(sentence)
                print(doc_sentence, '<->', nlp(compare_sentence1), doc_sentence.similarity(nlp(compare_sentence1)))
        count+=1


def extractTokens(string):
    #tokenisation
    doc = nlp(string)
    tokens= [X.text for X in doc]

    #removing stopwords
    stopWords = set(stopwords.words('english'))
    clean_words = []
    for token in tokens:
            if token not in stopWords:
                clean_words.append(token)   #removes "stop words", useless words such as 'the', 'and'... etc.
    stems=[stemmer.stem(X) for X in clean_words]
    return stems


def main():
    file1 = open('article.txt', 'r',encoding='utf8')
    stringarray = file1.readlines()
    CompanyName="Panasonic"
    #string="Japanese consumer electronics giant Panasonic has disclosed a security breach wherein an unauthorized third-party broke into its network and potentially accessed data from one of its file servers. As the result of an internal investigation, it was determined that some data on a file server had been accessed during the intrusion," the company said in a short statement published on November 26. Panasonic didn't reveal the exact nature of the data that was accessed, but TechCrunch reported that the breach began on June 22 and ended on November 3."
    #TestCompteurOccurences()
    #TestIdentifierSujet()
    #TestIdentifierDate()
    seperateBySentence(stringarray,CompanyName)
    

main()





##Pour trouver les mots similaires au mot cyberattack et les placer dans la liste keywords
#your_word = "cyberattack"
#ms = nlp.vocab.vectors.most_similar(np.asarray([nlp.vocab.vectors[nlp.vocab.strings[your_word]]]), n=10)
#keywords = []
#for word in ms[0][0]:
#    keywords.append(nlp.vocab.strings[word]) 
#distances = ms[2]
#print(keywords)

##Tester la similarité de deux phrases
#doc1 = nlp("PNB customers' data exposed for seven months du to server vulnerability")
#doc2 = nlp("Polish T-Mobile unit faces cyber attack, systems not compromised ")
#print(doc1, '<->', doc2, doc1.similarity(doc2))
#doc3 = nlp("5 Simple steps to protect your practice from cyberattacks")
#print(doc2, '<->', doc3, doc2.similarity(doc3))
##Résultats : 0.7528227008873364 et 0.7557642629789989, il montre les similarités dans le vocabulaire mais ne différencie pas le contexte

