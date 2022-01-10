#Le code se fera ici
#regarder un tuto sur git hub / git hub desktop
#installer les librairies nécessaires si non installées
# pip install bs4       pip install google      pip install spacy      pip install tweepy

# On commence par l'exemple de SolarWinds, grande entreprise de contrôle de systèmes informatiques, victime d'une Cyberattaque de grande ampleur en 2020.
# A priori nous aurons déjà nos sources prédéfinies et lorsque que nous nous intéresserons au statut d'une entreprise en particulier,
# nous parcourrons nos sources à l'aide de mots clé (dont le nom de l'entreprise).
# Cependant ici à titre de découverte du web scraping l'approche est un peu différente, nous automatisons le processus de recherche qu'une personne lamba ferait sur Google.
import requests, webbrowser
from bs4 import BeautifulSoup
from googlesearch import search
import spacy 
import csv
import tweepy
import datetime as dt
import pandas as pd
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
 
#-----------------------------------------------------------------------------Sites Web-----------------------------------------------------------------------------------------                
#L'idée est de créer un algorithme de scraping pour chaque source suivant une architecture commune selon le type de site
#On implémentera par la suite l'analyse de Texte

def ScrapeHackerNews(company): 
    URL="https://thehackernews.com/"
    found=False
    page_counter=0
    
    mainpage=requests.get(URL)
    if(mainpage.ok): 
        soup=BeautifulSoup(mainpage.text, "lxml") #On scrape la première page
        anchors=soup.find_all('a')
        for a in anchors:
            if(a.get('href') != None): #On vérifie que le href n'est pas nul
                if (company in a.get('href')) or (company in a.text):
                    newpage=requests.get(a.get('href'))
                    newsoup=BeautifulSoup(newpage.text, "lxml")
                    for paragraph in newsoup.find_all('p'):
                        print(paragraph.text)
                    found=True
                    print("Information found on "+a.get('href'))
                    #webbrowser.open(a.get('href'))
        while(found==False and page_counter<2): #Tant que l'on a pas trouvé ou scrapé moins de 2 pages, on scrape la page suivante.
            nextpageURL=""
            for a in anchors: #Recherche de la page suivante
                anchor=str(a)
                if(("Next" in anchor) or ("next" in anchor) or ("Page" in anchor) or ("page" in anchor) or \
                  ("Older" in anchor) or ("older" in anchor) ):
                    if(a['href'].startswith("https://")):
                        nextpageURL=a['href']
            if(nextpageURL!=""):
                page_counter=page_counter+1
                nextpage=requests.get(nextpageURL)
                if nextpage.ok:
                    #webbrowser.open(nextpageURL)
                    soup=BeautifulSoup(nextpage.text, "lxml")
                    anchors=soup.find_all('a')
                    for a in anchors:
                        if(a.get('href') != None):
                            if (company in a.get('href')) or (company in a.text):
                                newpage=requests.get(a.get('href'))
                                newsoup=BeautifulSoup(newpage.text, "lxml")
                                for paragraph in newsoup.find_all('p'):
                                    print(paragraph.text)
                                #webbrowser.open(a.get('href'))
                                found=True
                                print("Information found on "+a.get('href'))
                else: #Requête page suivante échoue, on sort de la boucle
                    print("Request Failure: "+nextpageURL)
                    break
            else: #Pas de page suivante, on sort de la boucle
                break
        if(found==False):
            print("Could not scrape any information about "+ company+" on "+URL)
    else: #L'URL de base est invalide
        print("Request Failure: "+URL)

def ScrapeDarkReading(company): #Site à scroll infini
    URL="https://www.darkreading.com/attacks-breaches"
    found=False
    page_counter=2
    
    mainpage=requests.get(URL)
    if(mainpage.ok): 
        soup=BeautifulSoup(mainpage.text, "lxml") #On scrape la première page
        anchors=soup.find_all('a')
        for a in anchors:
            if(a.get('href') != None): #On vérifie que le href n'est pas nul
                if (company in a.get('href')) or (company in a.text):
                    newpage=requests.get(a.get('href'))
                    newsoup=BeautifulSoup(newpage.text, "lxml")
                    for paragraph in newsoup.find_all('p'):
                        print(paragraph.text)
                    found=True
                    print("Information found on "+a.get('href'))
                    #webbrowser.open(a.get('href'))
        while(found==False and page_counter<6):#Tant que l'on a pas trouvé ou scrapé moins de 2 pages, on scrape la page suivante.
            nextpageURL="https://www.darkreading.com/attacks-breaches?page={}".format(page_counter)
            if(nextpageURL!=""):
                page_counter=page_counter+1
                nextpage=requests.get(nextpageURL)
                if nextpage.ok:
                    #webbrowser.open(nextpageURL)
                    soup=BeautifulSoup(nextpage.text, "lxml")
                    anchors=soup.find_all('a')
                    for a in anchors:
                        if(a.get('href') != None):
                            if (company in a.get('href')) or (company in a.text):
                                newpage=requests.get(a.get('href'))
                                newsoup=BeautifulSoup(newpage.text, "lxml")
                                for paragraph in newsoup.find_all('p'):
                                    print(paragraph.text)
                                #webbrowser.open(a.get('href'))
                                found=True
                                print("Information found on "+a.get('href'))
                else: #Requête page suivante échoue, on sort de la boucle
                    print("Request Failure: "+nextpageURL)
                    break
            else: #Pas de page suivante, on sort de la boucle
                break
        if(found==False):
            print("Could not scrape any information about "+ company+" on "+URL)
    else: #L'URL de base est invalide
        print("Request Failure: "+URL)

def ScrapeZDnet(company): #Reconstrucrtion d'URL nécessaire  --> stringObject[start:stop:interval]
    URL="https://www.zdnet.com/blog/security/"
    found=False
    page_counter=0

    mainpage=requests.get(URL)
    if(mainpage.ok): 
        soup=BeautifulSoup(mainpage.text, "lxml") #On scrape la première page
        anchors=soup.find_all('a')
        for a in anchors:
            anchor_link=a.get('href')
            if(anchor_link != None): #On vérifie que le href n'est pas nul
                if(anchor_link.startswith("/")): #On le reconsitue si besoin
                    anchor_link=anchor_link[1:] #Enlever le "/" du début
                    anchor_link=URL+anchor_link #Et ensuite le concaténer avec l'URL de base
                if (company in anchor_link) or (company in a.text):
                    newpage=requests.get(anchor_link)
                    newsoup=BeautifulSoup(newpage.text, "lxml")
                    for paragraph in newsoup.find_all('p'):
                        print(paragraph.text)
                    found=True
                    print("Information found on "+anchor_link)
                    #webbrowser.open(anchor_link)
        while(found==False and page_counter<2): #Tant que l'on a pas trouvé ou scrapé moins de 2 pages, on scrape la page suivante.
            nextpageURL=""
            for a in anchors:
                anchor=str(a)
                if("class=\"next\"" in anchor):
                    if(a['href'].startswith("https://")):
                        nextpageURL=a['href']
            if(nextpageURL!=""):
                page_counter=page_counter+1
                nextpage=requests.get(nextpageURL)
                if nextpage.ok:
                    #webbrowser.open(nextpageURL)
                    soup=BeautifulSoup(nextpage.text, "lxml")
                    anchors=soup.find_all('a')
                    for a in anchors:
                        anchor_link=a.get('href')
                        if(anchor_link != None):
                            if(anchor_link.startswith("/")): #On le reconsitue encore si besoin
                                anchor_link=anchor_link[1:]
                                anchor_link=URL+anchor_link
                            if (company in anchor_link) or (company in a.text):
                                newpage=requests.get(anchor_link)
                                newsoup=BeautifulSoup(newpage.text, "lxml")
                                for paragraph in newsoup.find_all('p'):
                                    print(paragraph.text)
                                #webbrowser.open(anchor_link)
                                found=True
                                print("Information found on "+anchor_link)
                else: #Requête page suivante échoue, on sort de la boucle
                    print("Request Failure: "+nextpageURL)
                    break
            else: #Pas de page suivante, on sort de la boucle
                break
        if(found==False):
            print("Could not scrape any information about "+ company+" on "+URL)
    else: #L'URL de base est invalide
        print("Request Failure: "+URL)

def ScrapeTechRP(company):
    URL="https://www.techrepublic.com/topic/security/"
    found=False
    page_counter=0
    
    mainpage=requests.get(URL)
    if(mainpage.ok): 
        soup=BeautifulSoup(mainpage.text, "lxml") #On scrape la première page
        anchors=soup.find_all('a')
        for a in anchors:
            if(a.get('href') != None): #On vérifie que le href n'est pas nul
                if (company in a.get('href')) or (company in a.text):
                    newpage=requests.get(a.get('href'))
                    newsoup=BeautifulSoup(newpage.text, "lxml")
                    for paragraph in newsoup.find_all('p'):
                        print(paragraph.text)
                    found=True
                    print("Information found on "+a.get('href'))
                    #webbrowser.open(a.get('href'))
        while(found==False and page_counter<2): #Tant que l'on a pas trouvé ou scrapé moins de 2 pages, on scrape la page suivante.
            nextpageURL=""
            for a in anchors: #Recherche de la page suivante
                anchor=str(a)
                if("<span>Next</span>" in anchor):
                    if(a['href'].startswith("https://")):
                        nextpageURL=a['href']
            if(nextpageURL!=""):
                page_counter=page_counter+1
                nextpage=requests.get(nextpageURL)
                if nextpage.ok:
                    #webbrowser.open(nextpageURL)
                    soup=BeautifulSoup(nextpage.text, "lxml")
                    anchors=soup.find_all('a')
                    for a in anchors:
                        if(a.get('href') != None):
                            if (company in a.get('href')) or (company in a.text):
                                newpage=requests.get(a.get('href'))
                                newsoup=BeautifulSoup(newpage.text, "lxml")
                                for paragraph in newsoup.find_all('p'):
                                    print(paragraph.text)
                                #webbrowser.open(a.get('href'))
                                found=True
                                print("Information found on "+a.get('href'))
                else: #Requête page suivante échoue, on sort de la boucle
                    print("Request Failure: "+nextpageURL)
                    break
            else: #Pas de page suivante, on sort de la boucle
                break
        if(found==False):
            print("Could not scrape any information about "+ company+" on "+URL)
    else: #L'URL de base est invalide
        print("Request Failure: "+URL)
 
def ScrapeMcAfee(company):
    URL="https://www.mcafee.com/blogs/other-blogs/mcafee-labs/"
    found=False
    page_counter=0

    mainpage=requests.get(URL)
    if(mainpage.ok): 
        soup=BeautifulSoup(mainpage.text, "lxml") #On scrape la première page
        anchors=soup.find_all('a')
        for a in anchors:
            if(a.get('href') != None): #On vérifie que le href n'est pas nul
                if (company in a.get('href')) or (company in a.text):
                    newpage=requests.get(a.get('href'))
                    newsoup=BeautifulSoup(newpage.text, "lxml")
                    for paragraph in newsoup.find_all('p'):
                        print(paragraph.text)
                    found=True
                    print("Information found on "+a.get('href'))
                    #webbrowser.open(a.get('href'))
        while(found==False and page_counter<2): #Tant que l'on a pas trouvé ou scrapé moins de 2 pages, on scrape la page suivante.
            nextpageURL=""
            for a in anchors: #Recherche de la page suivante
                anchor=str(a)
                if("class=\"next page-numbers\"" in anchor):
                    if(a['href'].startswith("https://")):
                        nextpageURL=a['href']
            if(nextpageURL!=""):
                page_counter=page_counter+1
                nextpage=requests.get(nextpageURL)
                if nextpage.ok:
                    #webbrowser.open(nextpageURL)
                    soup=BeautifulSoup(nextpage.text, "lxml")
                    anchors=soup.find_all('a')
                    for a in anchors:
                        if(a.get('href') != None):
                            if (company in a.get('href')) or (company in a.text):
                                newpage=requests.get(a.get('href'))
                                newsoup=BeautifulSoup(newpage.text, "lxml")
                                for paragraph in newsoup.find_all('p'):
                                    print(paragraph.text)
                                #webbrowser.open(a.get('href'))
                                found=True
                                print("Information found on "+a.get('href'))
                else: #Requête page suivante échoue, on sort de la boucle
                    print("Request Failure: "+nextpageURL)
                    break
            else: #Pas de page suivante, on sort de la boucle
                break
        if(found==False):
            print("Could not scrape any information about "+ company+" on "+URL)
    else: #L'URL de base est invalide
        print("Request Failure: "+URL)

def ScrapeGraham(company): #Définition de headers nécessaire
    URL="https://grahamcluley.com/"
    found=False
    page_counter=0
    headers={"User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"}

    mainpage=requests.get(URL, headers=headers)
    if(mainpage.ok): 
        soup=BeautifulSoup(mainpage.text, "lxml") #On scrape la première page
        anchors=soup.find_all('a')
        for a in anchors:
            if(a.get('href') != None): #On vérifie que le href n'est pas nul
                if (company in a.get('href')) or (company in a.text):
                    newpage=requests.get(a.get('href'), headers=headers)
                    newsoup=BeautifulSoup(newpage.text, "lxml")
                    for paragraph in newsoup.find_all('p'):
                        print(paragraph.text)
                    found=True
                    print("Information found on "+a.get('href'))
                    #webbrowser.open(a.get('href'))
        while(found==False and page_counter<2): #Tant que l'on a pas trouvé ou scrapé moins de 2 pages, on scrape la page suivante.
            nextpageURL=""
            for a in anchors: #Recherche de la page suivante
                anchor=str(a)
                if("class=\"nextpostslink\"" in anchor):
                    if(a['href'].startswith("https://")):
                        nextpageURL=a['href']
            if(nextpageURL!=""):
                page_counter=page_counter+1
                nextpage=requests.get(nextpageURL)
                if nextpage.ok:
                    #webbrowser.open(nextpageURL)
                    soup=BeautifulSoup(nextpage.text, "lxml")
                    anchors=soup.find_all('a')
                    for a in anchors:
                        if(a.get('href') != None):
                            if (company in a.get('href')) or (company in a.text):
                                newpage=requests.get(a.get('href'), headers=headers)
                                newsoup=BeautifulSoup(newpage.text, "lxml")
                                for paragraph in newsoup.find_all('p'):
                                    print(paragraph.text)
                                #webbrowser.open(a.get('href'))
                                found=True
                                print("Information found on "+a.get('href'))
                else: #Requête page suivante échoue, on sort de la boucle
                    print("Request Failure: "+nextpageURL)
                    break
            else: #Pas de page suivante, on sort de la boucle
                break
        if(found==False):
            print("Could not scrape any information about "+ company+" on "+URL)
    else: #L'URL de base est invalide
        print("Request Failure: "+URL)


def ScrapeITsecguru(company): #Scroll infini
    URL="https://www.itsecurityguru.org/news/"
    print("Nothing for now.")

def ScrapeCSO(company): #Reconstruciton d'URL nécessaire / Recherche de page suivante différente
    URL="https://www.csoonline.com/news-analysis/"
    found=False
    article_counter=0
    headers={"User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"}

    mainpage=requests.get(URL)
    if(mainpage.ok): 
        soup=BeautifulSoup(mainpage.text, "lxml") #On scrape la première page
        anchors=soup.find_all('a')
        for a in anchors:
            anchor_link=a.get('href')
            if(anchor_link != None): #On vérifie que le href n'est pas nul
                if(anchor_link.startswith("/")): #On le reconsitue si besoin
                    baseURL=URL[:25] #Dans ce site il faut enlever le "/news-analysis/" à la fin de l'URL de base
                    anchor_link=baseURL+anchor_link #Et ensuite le concaténer avec le href
                if (company in anchor_link) or (company in a.text):
                    newpage=requests.get(anchor_link)
                    newsoup=BeautifulSoup(newpage.text, "lxml")
                    for paragraph in newsoup.find_all('p'):
                        print(paragraph.text)
                    found=True
                    print("Information found on "+anchor_link)
                    #webbrowser.open(anchor_link)
        while(found==False and article_counter<20): #Tant que l'on a pas trouvé ou scrapé moins de 2 pages, on scrape la page suivante. (1 page correspond à 20 articles ici, la premiere page allant de 0 à 20).
            article_counter=article_counter+20
            nextpageURL=URL+"?start="+str(article_counter)
            nextpage=requests.get(nextpageURL)
            if nextpage.ok:
                #webbrowser.open(nextpageURL)
                soup=BeautifulSoup(nextpage.text, "lxml")
                anchors=soup.find_all('a')
                for a in anchors:
                    anchor_link=a.get('href')
                    if(anchor_link != None):
                        if(anchor_link.startswith("/")): #On le reconsitue encore si besoin
                            baseURL=URL[:25]
                            anchor_link=baseURL+anchor_link
                        if (company in anchor_link) or (company in a.text):
                            newpage=requests.get(anchor_link)
                            newsoup=BeautifulSoup(newpage.text, "lxml")
                            for paragraph in newsoup.find_all('p'):
                                print(paragraph.text)
                            #webbrowser.open(anchor_link)
                            found=True
                            print("Information found on "+anchor_link)
            else: #Requête page suivante échoue, on sort de la boucle
                print("Request Failure: "+nextpageURL)
                break
        if(found==False):
            print("Could not scrape any information about "+ company+" on "+URL)
    else: #L'URL de base est invalide
        print("Request Failure: "+URL)

#-----------------------------------------------------------------------------Twitter-------------------------------------------------------------------------------------------
#Quelques libraries pour scraper Twitter:
#twint ->https://github.com/twintproject/twint/wiki/Configuration (semble ne pas fonctionner)
#twitterscraper -> https://github.com/taspinar/twitterscraper (semble ne pas fonctionner non plus)
#Nous allons utiliser ici l'API standard de twitter (voir "API Twitter.txt") https://developer.twitter.com/en/docs/twitter-api/getting-started/about-twitter-api || https://developer.twitter.com/en/portal/dashboard
#documentation->https://docs.tweepy.org/en/stable/client.html  /!\ Limite de 500k tweets par mois


def ScrapeTwitter(company):

    consumer_key="SZ4ZCDWtAOi0n5KwX2pHesboZ"
    consumer_secret="dOOFcSAC0mlJjG0tLl2yCXCSbUOGEEwnoeGPXcqScMWk0ApH1c"
    access_token="1478730189194600452-UEAxcfNAJhEYOJ6cwNhRnBni9AmRvP"
    access_token_secret="bHbPra26P0VWCZxTAtG2blyjSPDvtN8N6l5p3VGIq5qLD"

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.Client(auth)

    twitter_accounts=["threatpostmoiuphnàozieur", "briankrebs", "peterkruse"] #On met ici les noms utilisateurs de type: "@exemple" (sans le @)
    found=False

    for username in twitter_accounts:
        print("Nothing for now.")
        
                

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def WebScraping(company): #Attention, la recherche est case sensitive! (exemple: Microsoft!=microsoft)
    ScrapeHackerNews(company)
    ScrapeDarkReading(company) 
    ScrapeZDnet(company)
    ScrapeTechRP(company)
    ScrapeMcAfee(company)
    ScrapeGraham(company)
    #ScrapeITsecguru(company) #Ne fonctionne pas encore
    ScrapeCSO(company)
    #ScrapeTwitter(company) Ne fonctionne pas encore


def main():
    #print("Hello World!") #Remplacer cette ligne par la fonction à executer.
    WebScraping("Logapalooza")

main()

# PS: Lorsque vous voulez que votre code trouve un élément en particulier de la page, faire un clique droit -> inspecter pour trouver l'élément html correspondant 
# et utiliser soup.find("nom de l'élément"). Pour plus d'infos sur html https://developer.mozilla.org/fr/docs/Web/HTML/Element
# Si vous souhaitez enregistrer du code test sans risquer de détruire le code principal vous pouvez toujours créer une nouvelle branche séparée de la branche main et y téléverser votre code.
# (/!\ Lorsque vous changez de branche et revenez à la branche principale ne les fusionnez pas à moins d'être sûr de la validité du code ajouté!)
