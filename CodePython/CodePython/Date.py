import requests, webbrowser
from bs4 import BeautifulSoup
from googlesearch import search
import spacy
from htmldate import find_date
#CMD
#pip install htmldate
from googletrans import Translator
#CMD
##pip install googletrans==4.0.0-rc1
import pandas
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
#CMD
#pip install nltk

#Python console
#import nltk
#nltk.download('stopwords')

#CMD
#python -m spacy download en_core_web_sm
#python -m spacy download fr_core_news_sm

def translate(string):  #return true if text is french, false if english. Translates into english other language
    french=True
    translator = Translator(service_urls=[
      'translate.google.com',
      'translate.google.fr',
    ])
    dec_lan = translator.detect(string)
    print(dec_lan)
    if dec_lan.lang=='fr':
        french=True
    elif dec_lan.lang=='en':
        french=False
    else:
        french=False
        string=translator.translate(string, src=dec_lan, dest='en')
    return french

def extractTokens(string,french):
    if(french):
        nlp = spacy.load("fr_core_news_sm")
    else:
        nlp = spacy.load("en_core_web_sm")
    doc = nlp(string)
    return [X.text for X in doc]

def removestopwords(test,french):
    if(french):
        stopWords = set(stopwords.words('french'))
    else:
        stopWords = set(stopwords.words('english'))
    clean_words = []
    for token in test:
            if token not in stopWords:
                clean_words.append(token)   #removes "stop words", useless words such as 'the', 'and'... etc.
    return clean_words

def final(string):
    french=translate(string)
    token=extractTokens(string,french)
    token2=removestopwords(token,french)
    print(token2)




def return_stem(sentence):
    doc = nlp(sentence)
    return [stemmer.stem(X.text) for X in doc]

def date():
    query= "SolarWinds Cyberattaque"
    links =[]
    dates =[]
    for j in search(query, num=10, stop=10, pause=0.5,tbs="qdr:m"): #10 derniers résultats du mois.
        print(j)
        links.append(j)
        try:
            dates.append(find_date(j))
        except:
            print("Pas de date html.")
            #find date with beautifulsoup

if __name__ == '__main__':
    translate()