#Le code se fera ici
#regarder un tuto sur git hub / git hub desktop
#installer les librairies nécessaires si non installées
# pip install bs4       pip install google      pip install spacy

# On commence par l'exemple de SolarWinds, grande entreprise de contrôle de systèmes informatiques, victime d'une Cyberattaque de grande ampleur en 2020.
# A priori nous aurons déjà nos sources prédéfinies et lorsque que nous nous intéresserons au statut d'une entreprise en particulier,
# nous parcourrons nos sources à l'aide de mots clé (dont le nom de l'entreprise).
# Cependant ici à titre de découverte du web scraping l'approche est un peu différente, nous automatisons le processus de recherche qu'une personne lamba ferait sur Google.
import requests, webbrowser
from bs4 import BeautifulSoup
from googlesearch import search
import spacy 
nlp = spacy.load('en_core_web_sm') #python -m spacy download en

def introwebscraping():
    query= "SolarWinds Cyberattaque" #La recherche que l'on effectue sur Google
    links =[] #Liste qui contiendra tous les liens des sites webs que nous allons "scraper" à l'issue de la recherche.

    for j in search(query, num=3, stop=3, pause=0.5): #On se contente des 3 résultats jugés les plus pertinents par Google dans cet exemple, idéalement en prendre le plus possible.
    #print(j)
        webbrowser.open(j)
        links.append(j) #On sauvegarde les liens

    for link in links:
        print("-------------------------------------------------------------------------------------------------------------------------------------------------------")
        page=requests.get(link)
        soup=BeautifulSoup(page.text, "lxml")  #Lecture du code source de la page
        print(link+"\n")
        print(soup.find("title").text+"\n") #Titre de la page (à priori un article)
        paragraphs=soup.find_all("p")
        keywords=["cyberattaque"] #mots clé pour nous aider à extraire l'information voulue
        keysentences=[] #phrases clé qu'il faudra analyser 
        for paragraph in paragraphs: #Parcourir les paragraphes pour en extraire les informations relatives à une attaque ou faille de sécurité.
            c=nlp(paragraph.text) #Conversion du texte en un objet spacy
            sentences=list(c.sents) 
            for sentence in sentences:
                for keyword in keywords:
                    if keyword in str(sentence):
                        print(sentence)
                        keysentences.append(sentence)
                        

def webscraping(company): #/!\ La recherche est Case sensitive (les majuscules/minuscules sont différenciées)
    #(Peut-être) Faire un pattern tel que: 
    #1 Dans un premier temps on regarde si l'entreprise apparait dans la page
    #2 Si elle apparait dans un bloc qui mène à un lien, ouvrir le lien pour scraper la nouvelle page
    #Le but est de créer un programme général de manière à pouvoir ajouter les sources au fur et à mesure.

    sources=["https://www.darkreading.com/attacks-breaches",
             "https://thehackernews.com/"] #On part du principe que nos sources sont fiables ici  (les ajouter et tester au fur et à mesure)

    for source in sources:
        #print(source+"\n")
        mainpage=requests.get(source)
        soup=BeautifulSoup(mainpage.text, "lxml")
        anchors=soup.find_all('a')
        for a in anchors:
            if (company in a.get('href')) or (company in a.text):
                newpage=requests.get(a.get('href'))
                newsoup=BeautifulSoup(newpage.text, "lxml")
                for paragraph in newsoup.find_all('p'):
                    print(paragraph.text)
                #webbrowser.open(a.get('href'))
            elif(" Next Page" in a.text): 
                newpage=requests.get(a.get('href'))
                webbrowser.open(a.get('href'))
           #else open and scrap the next page (until when do we open the next page?) or keep scrolling down (again, until when?)
        #print("\n---------------------------------------------------------------------------------------------------------------------------\n")



def main():
    #print("Hello World!") #Remplacer cette ligne par la fonction à executer.
    webscraping("Celo")


main()

#salut
# PS: Lorsque vous voulez que votre code trouve un élément en particulier de la page, faire un clique droit -> inspecter pour trouver l'élément html correspondant 
# et utiliser soup.find("nom de l'élément"). Pour plus d'infos sur html https://developer.mozilla.org/fr/docs/Web/HTML/Element
# Si vous souhaitez enregistrer du code test sans risquer de détruire le code principal vous pouvez toujours créer une nouvelle branche séparée de la branche main et y téléverser votre code.
# (/!\ Lorsque vous changez de branche et revenez à la branche principale ne les fusionnez pas à moins d'être sûr de la validité du code ajouté!)

#Recherche Twitter

import tweepy
import pandas as pd

#Crée un client avec les clés de l'API Twitter
def getClient():
    client = tweepy.Client(bearer_token = 'AAAAAAAAAAAAAAAAAAAAABmhVwEAAAAADleMPpAu4nrN%2B5GK%2BPtKRcBh%2FX8%3D6Dy7xUEHppi5vEKwh3fqQs4PVp2ZfoTaxtq18YFePWxYfLJMZh',
                            consumer_key = "Qu5Qic0NMdaOJCqpcPwaefeum",
                            consumer_secret = "sgLdwgLaDuTZ9dMaFkBZAH5AgRpYiaRSE8AHhpjDZyNiSXbUuG",
                            access_token = "1461094274922131459-R7LncaRgehVA1HKwZBQQUNlCE94N2M",
                            access_token_secret = "ZguIMFulZFAiRqzngznsnJtkudvqwFoqevZuuPynvMQ3l")
    return client

#Recherche sur twitter des mots clés et renvoie un tableau des tweets les plus récents (au max 15 tweets)
def RechercheTweetsRecents(query):
    client = getClient()
    searchResults = client.search_recent_tweets(query=query, max_results = 15)

    tweets = searchResults.data

    results=[]

    if tweets is not None and len(tweets) != 0:
        for tweet in tweets:
            temp = {}
            temp['id'] = tweet.id
            temp['text'] = tweet.text
            results.append(temp) #results est un tableau de dictionnaires
    
    return results

#Test de la fonction RechercheTweetsRecents
#tweets = RechercheTweetsRecents("cyberattaque")
#for tweet in tweets:
#    print(tweet)

import requests
import json

#Pour rechercher les tweets d'un utilisateur précis, il faut récupérer son id
def getUserId(username):
    url = 'https://api.twitter.com/2/users/by/username/{}'.format(username)

    bearer_token = 'AAAAAAAAAAAAAAAAAAAAABmhVwEAAAAADleMPpAu4nrN%2B5GK%2BPtKRcBh%2FX8%3D6Dy7xUEHppi5vEKwh3fqQs4PVp2ZfoTaxtq18YFePWxYfLJMZh'
    headers = {'Authorization': 'Bearer {}'.format(bearer_token)}

    #on extrait le profil du user
    response = requests.request('GET', url, headers = headers)
    response = response.json()
    #response = {'data': {'id': '22790881', 'name': 'briankrebs', 'username': 'briankrebs'}}
    id = response['data']['id'] #On récupère l'id dans le dictionnaire response
    
    return id

import requests
import json

#test getUserId
#username = 'briankrebs'
#print(getUserId(username))

#Recherche parmis les n derniers tweets de l'utilisateur s'il a mentionné un des mots clés du tableau keywords
def RechercheTweetsUser(username, keywords):
    id = getUserId(username)
    mention = False #Si l'on a trouvé un tweet à propos de l'attaque à confirmer

    url = 'https://api.twitter.com/2/users/{}/tweets'.format(id)
    #le bearer_token permet de se connecter à l'API de twitter
    bearer_token = 'AAAAAAAAAAAAAAAAAAAAABmhVwEAAAAADleMPpAu4nrN%2B5GK%2BPtKRcBh%2FX8%3D6Dy7xUEHppi5vEKwh3fqQs4PVp2ZfoTaxtq18YFePWxYfLJMZh'
    headers = {'Authorization': 'Bearer {}'.format(bearer_token)}

    response = requests.request('GET', url, headers = headers)

    tweetsData = response.json()
    ListAlarmingTweets = []
    
    for tweetData in tweetsData['data']:
        tweetText = tweetData['text']
        for keyword in keywords:
            if(keyword in tweetText):
                ListAlarmingTweets.append(tweetData)
                mention = True
                print(tweetData)
                
    return mention


username = 'briankrebs'
RechercheTweetsUser(username, 'a')