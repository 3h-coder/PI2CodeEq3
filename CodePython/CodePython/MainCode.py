#Le code se fera ici
#regarder un tuto sur git hub / git hub desktop
#installer les librairies nécessaires si non installées
# pip install bs4       pip install google      pip install spacy      pip install tweepy      pip install pickle

import requests, webbrowser
from bs4 import BeautifulSoup
from googlesearch import search
import spacy 
import csv
import tweepy
import json
import datetime as dt
import pandas as pd
import pickle
import dateparser
import warnings
from TextAnalyzer import TextAnalyzer
nlp = spacy.load('en_core_web_sm') #python -m spacy download en
warnings.filterwarnings("ignore", message="The localize method is no longer necessary, as this time zone supports the fold attribute")

# On commence par l'exemple de SolarWinds, grande entreprise de contrôle de systèmes informatiques, victime d'une Cyberattaque de grande ampleur en 2020.
# A priori nous aurons déjà nos sources prédéfinies et lorsque que nous nous intéresserons au statut d'une entreprise en particulier,
# nous parcourrons nos sources à l'aide de mots clé (dont le nom de l'entreprise).
# Cependant ici à titre de découverte du web scraping l'approche est un peu différente, nous automatisons le processus de recherche qu'une personne lamba ferait sur Google.
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

def SoupTest():
    URL="https://thehackernews.com/"
    mainpage=requests.get(URL)
    soup=BeautifulSoup(mainpage.text, "lxml") #On scrape la première page
    anchors=soup.find_all('a', {"class": "story-link"})
    for a in anchors:
        titles=a.find_all('h2')
        for title in titles:
            print(title.text)

def ScrapeHackerNews(company): 
    URL="https://thehackernews.com/"
    found=False
    page_counter=1
    
    mainpage=requests.get(URL)
    if(mainpage.ok): 
        soup=BeautifulSoup(mainpage.text, "lxml") #On scrape la première page
        anchors=soup.find_all('a', {"class": "story-link"})
        link_found=""
        for a in anchors:
            if(a.get('href') != None and a.get('href')!=link_found): #On vérifie que le href n'est pas nul et que l'on ne retombe pas sur le même lien
                title=a.find('h2')
                if (company in a.get('href')) or (company in a.text) or (company.lower() in a.get('href')) \
                or (company.capitalize() in a.get('href')) or (company.capitalize() in a.text) \
                or (company.lower() in a.text) or (company in title.text) or (company.lower() in title.text) or (company.capitalize() in title.text):
                    link_found=a.get('href')
                    article_date=a.find('i', {"class": "icon-font icon-calendar"}).next_sibling #On extrait la date de l'article qu'il faudra ensuite formater
                    article_date=dateparser.parse(article_date).date()
                    newpage=requests.get(a.get('href'))
                    newsoup=BeautifulSoup(newpage.text, "lxml")
                    article=""
                    for paragraph in newsoup.find_all('p'):
                        article+="\n"+paragraph.text
                    ta=TextAnalyzer(company, article, link_found, article_date) #On crée notre objet analyseur de texte
                    ta.RunAnalysis() #On procède à l'analyse de l'article pour déterminer le statut de cybersécurité de l'entreprise
                    found=True
                    print("Information found on "+a.get('href'))
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
                    soup=BeautifulSoup(nextpage.text, "lxml")
                    anchors=soup.find_all('a',{"class": "story-link"})
                    for a in anchors:
                        if(a.get('href') != None and a.get('href')!=link_found):
                            title=a.find('h2')
                            if (company in a.get('href')) or (company in a.text) or (company.lower() in a.get('href')) \
                            or (company.capitalize() in a.get('href')) or (company.capitalize() in a.text) \
                            or (company.lower() in a.text) or (company in title.text) or (company.lower() in title.text) or (company.capitalize() in title.text):
                                link_found=a.get('href')
                                article_date=a.find('i', {"class": "icon-font icon-calendar"}).next_sibling
                                article_date=dateparser.parse(article_date).date()
                                newpage=requests.get(a.get('href'))
                                newsoup=BeautifulSoup(newpage.text, "lxml")
                                article=""
                                for paragraph in newsoup.find_all('p'):
                                    article+="\n"+paragraph.text
                                ta=TextAnalyzer(company, article, link_found, article_date) 
                                ta.RunAnalysis()
                                found=True
                                print("Information found on "+a.get('href'))
                else: #Requête page suivante échoue, on sort de la boucle
                    print("Request Failure: "+nextpageURL+" returned: "+nextpage)
                    break
            else: #Pas de page suivante, on sort de la boucle
                break
        if(found==False):
            print("Could not scrape any information about "+ company+" on "+URL)
    else: #L'URL de base est invalide
        print("Request Failure: "+URL+" returned: "+mainpage)

def ScrapeDarkReading(company): #Site à scroll infini
    URL="https://www.darkreading.com/attacks-breaches"
    found=False
    page_counter=2
    
    mainpage=requests.get(URL)
    if(mainpage.ok): 
        soup=BeautifulSoup(mainpage.text, "lxml") #On scrape la première page
        anchors=soup.find_all('a')
        link_found=""
        for a in anchors:
            if(a.get('href') != None and a.get('href')!=link_found): #On vérifie que le href n'est pas nul et que l'on ne retombe pas sur le même lien
                if (company in a.get('href')) or (company in a.text) or (company.lower() in a.get('href')) or (company.lower() in a.text) \
                or (company.capitalize() in a.get('href')) or (company.capitalize() in a.text):
                    link_found=a.get('href')
                    wrapper=a.parent.parent
                    article_date=(wrapper.find("div", {"class": "d-md-none arcile-date"}).text) #On extrait la date de l'article qu'il faudra ensuite formater
                    article_date=dateparser.parse(article_date).date()
                    newpage=requests.get(a.get('href'))
                    newsoup=BeautifulSoup(newpage.text, "lxml")
                    article=""
                    for paragraph in newsoup.find_all('p'):
                        article+="\n"+paragraph.text
                    ta=TextAnalyzer(company, article, link_found, article_date) #On crée notre objet analyseur de texte
                    ta.RunAnalysis() #On procède à l'analyse de l'article pour déterminer le statut de cybersécurité de l'entreprise
                    found=True
                    print("Information found on "+a.get('href'))
        while(found==False and page_counter<6):#Tant que l'on a pas trouvé ou scrapé moins de 2 pages, on scrape la page suivante.
            nextpageURL="https://www.darkreading.com/attacks-breaches?page={}".format(page_counter)
            if(nextpageURL!=""):
                page_counter=page_counter+1
                nextpage=requests.get(nextpageURL)
                if nextpage.ok:
                    soup=BeautifulSoup(nextpage.text, "lxml")
                    anchors=soup.find_all('a')
                    for a in anchors:
                        if(a.get('href') != None and a.get('href')!=link_found):
                            if (company in a.get('href')) or (company in a.text) or (company.lower() in a.get('href')) or (company.lower() in a.text) \
                            or (company.capitalize() in a.get('href')) or (company.capitalize() in a.text):
                                link_found=a.get('href')
                                wrapper=a.parent.parent
                                article_date=(wrapper.find("div", {"class": "d-md-none arcile-date"}).text)
                                article_date=dateparser.parse(article_date).date()
                                newpage=requests.get(a.get('href'))
                                newsoup=BeautifulSoup(newpage.text, "lxml")
                                article=""
                                for paragraph in newsoup.find_all('p'):
                                    article+="\n"+paragraph.text
                                ta=TextAnalyzer(company, article, link_found, article_date) 
                                ta.RunAnalysis() 
                                found=True
                                print("Information found on "+a.get('href'))
                else: #Requête page suivante échoue, on sort de la boucle
                    print("Request Failure: "+nextpageURL+" returned: "+nextpage)
                    break
            else: #Pas de page suivante, on sort de la boucle
                break
        if(found==False):
            print("Could not scrape any information about "+ company+" on "+URL)
    else: #L'URL de base est invalide
        print("Request Failure: "+URL+" returned: "+mainpage)

def ScrapeZDnet(company): #Reconstrucrtion d'URL nécessaire  --> stringObject[start:stop:interval]
    URL="https://www.zdnet.com/blog/security/"
    found=False
    page_counter=1

    mainpage=requests.get(URL)
    if(mainpage.ok): 
        soup=BeautifulSoup(mainpage.text, "lxml") #On scrape la première page
        anchors=soup.find_all('a')
        link_found=""
        for a in anchors:
            anchor_link=a.get('href')
            if(a.get('href') != None and a.get('href')!=link_found): #On vérifie que le href n'est pas nul et que l'on ne retombe pas sur le même lien
                if(anchor_link.startswith("/")): #On le reconsitue si besoin
                    anchor_link=anchor_link[1:] #Enlever le "/" du début
                    anchor_link=URL+anchor_link #Et ensuite le concaténer avec l'URL de base
                if (company in a.get('href')) or (company in a.text) or (company.lower() in a.get('href')) or (company.lower() in a.text) \
                or (company.capitalize() in a.get('href')) or (company.capitalize() in a.text):
                    link_found=a.get('href')
                    wrapper=a.parent.parent
                    article_date=wrapper.find('p', {"class":"meta"}).find('span')['data-date'] #On extrait la date de l'article qu'il faudra ensuite formater
                    article_date=dateparser.parse(article_date).date()
                    print(article_date)
                    newpage=requests.get(anchor_link)
                    newsoup=BeautifulSoup(newpage.text, "lxml")
                    article=""
                    for paragraph in newsoup.find_all('p'):
                        article+="\n"+paragraph.text
                    ta=TextAnalyzer(company, article, link_found, article_date) #On crée notre objet analyseur de texte
                    ta.RunAnalysis() #On procède à l'analyse de l'article pour déterminer le statut de cybersécurité de l'entreprise
                    found=True
                    print("Information found on "+anchor_link)
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
                    soup=BeautifulSoup(nextpage.text, "lxml")
                    anchors=soup.find_all('a')
                    for a in anchors:
                        anchor_link=a.get('href')
                        if(anchor_link != None and a.get('href')!=link_found):
                            if(anchor_link.startswith("/")): #On le reconsitue encore si besoin
                                anchor_link=anchor_link[1:]
                                anchor_link=URL+anchor_link
                            if (company in a.get('href')) or (company in a.text) or (company.lower() in a.get('href')) or (company.lower() in a.text) \
                            or (company.capitalize() in a.get('href')) or (company.capitalize() in a.text):
                                link_found=a.get('href')
                                wrapper=a.parent.parent
                                article_date=wrapper.find('p', {"class":"meta"}).find('span')['data-date']
                                article_date=dateparser.parse(article_date).date()
                                newpage=requests.get(anchor_link)
                                newsoup=BeautifulSoup(newpage.text, "lxml")
                                article=""
                                for paragraph in newsoup.find_all('p'):
                                    article+="\n"+paragraph.text
                                ta=TextAnalyzer(company, article, link_found, article_date) 
                                ta.RunAnalysis() 
                                found=True
                                print("Information found on "+anchor_link)
                else: #Requête page suivante échoue, on sort de la boucle
                    print("Request Failure: "+nextpageURL+" returned: "+nextpage)
                    break
            else: #Pas de page suivante, on sort de la boucle
                break
        if(found==False):
            print("Could not scrape any information about "+ company+" on "+URL)
    else: #L'URL de base est invalide
        print("Request Failure: "+URL+" returned: "+mainpage)

def ScrapeTechRP(company):
    URL="https://www.techrepublic.com/topic/security/"
    found=False
    page_counter=1
    
    mainpage=requests.get(URL)
    if(mainpage.ok): 
        soup=BeautifulSoup(mainpage.text, "lxml") #On scrape la première page
        anchors=soup.find_all('a')
        link_found="" #si l'on trouve quelque chose on enregistre le lien dans cette variable
        for a in anchors:
            if(a.get('href') != None and a.get('href')!=link_found): #On vérifie que le href n'est pas nul et que l'on ne retombe pas sur le même lien
                if (company in a.get('href')) or (company in a.text) or (company.lower() in a.get('href')) or (company.lower() in a.text) \
                or (company.capitalize() in a.get('href')) or (company.capitalize() in a.text):
                    link_found=a.get('href')
                    newpage=requests.get(a.get('href'))
                    newsoup=BeautifulSoup(newpage.text, "lxml")
                    wrapper=a.parent
                    span=wrapper.find('span',{"class":"separator"})
                    article_date=wrapper.find('span',{"class":"separator"}).next_sibling.strip() #On extrait la date de l'article qu'il faudra ensuite formater
                    article_date=dateparser.parse(article_date).date()
                    article=""
                    for paragraph in newsoup.find_all('p'):
                        article+="\n"+paragraph.text
                    ta=TextAnalyzer(company, article, link_found, article_date) #On crée notre objet analyseur de texte
                    ta.RunAnalysis() #On procède à l'analyse de l'article pour déterminer le statut de cybersécurité de l'entreprise
                    found=True
                    print("Information found on "+a.get('href'))
        while(found==False and page_counter<2): #Tant que l'on a pas trouvé ou scrapé moins de 2 pages, on scrape la page suivante en répétant les mêmes étapes.
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
                    soup=BeautifulSoup(nextpage.text, "lxml")
                    anchors=soup.find_all('a')
                    for a in anchors:
                        if(a.get('href') != None and a.get('href')!=link_found):
                            link_found=a.get('href')
                            if (company in a.get('href')) or (company in a.text) or (company.lower() in a.get('href')) or (company.lower() in a.text) \
                            or (company.capitalize() in a.get('href')) or (company.capitalize() in a.text):
                                newpage=requests.get(a.get('href'))
                                newsoup=BeautifulSoup(newpage.text, "lxml")
                                wrapper=a.parent
                                span=wrapper.find('span',{"class":"separator"})
                                article_date=wrapper.find('span',{"class":"separator"}).next_sibling.strip() #On extrait la date de l'article qu'il faudra ensuite formater
                                article_date=dateparser.parse(article_date).date()
                                article=""
                                for paragraph in newsoup.find_all('p'):
                                    article+="\n"+paragraph.text
                                ta=TextAnalyzer(company, article, link_found, article_date) 
                                ta.RunAnalysis() 
                                found=True
                                print("Information found on "+a.get('href'))
                else: #Requête page suivante échoue, on sort de la boucle
                    print("Request Failure: "+nextpageURL+" returned: "+nextpage)
                    break
            else: #Pas de page suivante, on sort de la boucle
                break
        if(found==False):
            print("Could not scrape any information about "+ company+" on "+URL)
    else: #L'URL de base est invalide
        print("Request Failure: "+URL+" returned: "+mainpage)
 
def ScrapeMcAfee(company):
    URL="https://www.mcafee.com/blogs/other-blogs/mcafee-labs/"
    found=False
    page_counter=1

    mainpage=requests.get(URL)
    if(mainpage.ok): 
        soup=BeautifulSoup(mainpage.text, "lxml") #On scrape la première page
        anchors=soup.find_all('a')
        link_found=""
        for a in anchors:
            if(a.get('href') != None and a.get('href')!=link_found): #On vérifie que le href n'est pas nul et que l'on ne retombe pas sur le même lien
                if (company in a.get('href')) or (company in a.text) or (company.lower() in a.get('href')) or (company.lower() in a.text) \
                or (company.capitalize() in a.get('href')) or (company.capitalize() in a.text):
                    link_found=a.get('href')
                    wrapper=a.find_parent('div', {"class":"card"})
                    article_date=wrapper.find('small', {"class":"text-muted"}).text #On extrait la date de l'article qu'il faudra ensuite formater
                    article_date=dateparser.parse(article_date).date()
                    newpage=requests.get(a.get('href'))
                    newsoup=BeautifulSoup(newpage.text, "lxml")
                    article=""
                    for paragraph in newsoup.find_all('p'):
                        article+="\n"+paragraph.text
                    ta=TextAnalyzer(company, article, link_found, article_date) #On crée notre objet analyseur de texte
                    ta.RunAnalysis() #On procède à l'analyse de l'article pour déterminer le statut de cybersécurité de l'entreprise
                    found=True
                    print("Information found on "+a.get('href'))
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
                    soup=BeautifulSoup(nextpage.text, "lxml")
                    anchors=soup.find_all('a')
                    for a in anchors:
                        if(a.get('href') != None and a.get('href')!=link_found):
                            if (company in a.get('href')) or (company in a.text) or (company.lower() in a.get('href')) or (company.lower() in a.text) \
                            or (company.capitalize() in a.get('href')) or (company.capitalize() in a.text):
                                link_found=a.get('href')
                                wrapper=a.find_parent('div', {"class":"card"})
                                article_date=wrapper.find('small', {"class":"text-muted"}).text
                                article_date=dateparser.parse(article_date).date()
                                newpage=requests.get(a.get('href'))
                                newsoup=BeautifulSoup(newpage.text, "lxml")
                                article=""
                                for paragraph in newsoup.find_all('p'):
                                    article+="\n"+paragraph.text
                                ta=TextAnalyzer(company, article, link_found, article_date) 
                                ta.RunAnalysis() 
                                found=True
                                print("Information found on "+a.get('href'))
                else: #Requête page suivante échoue, on sort de la boucle
                    print("Request Failure: "+nextpageURL+" returned: "+nextpage)
                    break
            else: #Pas de page suivante, on sort de la boucle
                break
        if(found==False):
            print("Could not scrape any information about "+ company+" on "+URL)
    else: #L'URL de base est invalide
        print("Request Failure: "+URL+" returned: "+mainpage)

def ScrapeGraham(company): #Définition de headers nécessaire
    URL="https://grahamcluley.com/"
    found=False
    page_counter=1
    headers={"User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"}

    mainpage=requests.get(URL, headers=headers)
    if(mainpage.ok): 
        soup=BeautifulSoup(mainpage.text, "lxml") #On scrape la première page
        anchors=soup.find_all('a')
        link_found=""
        for a in anchors:
            if(a.get('href') != None and a.get('href')!=link_found): #On vérifie que le href n'est pas nul et que l'on ne retombe pas sur le même lien
                if (company in a.get('href')) or (company in a.text) or (company.lower() in a.get('href')) or (company.lower() in a.text) \
                or (company.capitalize() in a.get('href')) or (company.capitalize() in a.text):
                    link_found=a.get('href')
                    newpage=requests.get(a.get('href'), headers=headers)
                    newsoup=BeautifulSoup(newpage.text, "lxml")
                    wrapper=a.find_parent('header', {"class":"entry-header"})
                    article_date=wrapper.find('span', {"class":"post-date"}).text #On extrait la date de l'article qu'il faudra ensuite formatter
                    article_date=dateparser.parse(article_date).date()
                    article=""
                    for paragraph in newsoup.find_all('p'):
                        article+="\n"+paragraph.text
                    ta=TextAnalyzer(company, article, link_found, article_date) #On crée notre objet analyseur de texte
                    ta.RunAnalysis() #On procède à l'analyse de l'article pour déterminer le statut de cybersécurité de l'entreprise
                    found=True
                    print("Information found on "+a.get('href'))
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
                    soup=BeautifulSoup(nextpage.text, "lxml")
                    anchors=soup.find_all('a')
                    for a in anchors:
                        if(a.get('href') != None):
                            if (company in a.get('href')) or (company in a.text) or (company.lower() in a.get('href')) or (company.lower() in a.text) \
                            or (company.capitalize() in a.get('href')) or (company.capitalize() in a.text):
                                link_found=a.get('href')
                                newpage=requests.get(a.get('href'), headers=headers)
                                newsoup=BeautifulSoup(newpage.text, "lxml")
                                wrapper=a.find_parent('header', {"class":"entry-header"})
                                article_date=wrapper.find('span', {"class":"post-date"}).text
                                article_date=dateparser.parse(article_date).date()
                                article=""
                                for paragraph in newsoup.find_all('p'):
                                    article+="\n"+paragraph.text
                                ta=TextAnalyzer(company, article, link_found, article_date) 
                                ta.RunAnalysis() 
                                found=True
                                print("Information found on "+a.get('href'))
                else: #Requête page suivante échoue, on sort de la boucle
                    print("Request Failure: "+nextpageURL+" returned: "+nextpage)
                    break
            else: #Pas de page suivante, on sort de la boucle
                break
        if(found==False):
            print("Could not scrape any information about "+ company+" on "+URL)
    else: #L'URL de base est invalide
        print("Request Failure: "+URL+" returned: "+mainpage)

def ScrapeITsecguru(company): #Scroll infini
    URL="https://www.itsecurityguru.org/news/"
    print("Nothing for now.")

def ScrapeCSO(company): #Reconstruciton d'URL nécessaire / Recherche de page suivante différente
    URL="https://www.csoonline.com/news-analysis/"
    found=False
    article_counter=0

    mainpage=requests.get(URL)
    if(mainpage.ok): 
        soup=BeautifulSoup(mainpage.text, "lxml") #On scrape la première page
        anchors=soup.find_all('a')
        link_found=""
        for a in anchors:
            anchor_link=a.get('href')
            if(a.get('href') != None and a.get('href')!=link_found): #On vérifie que le href n'est pas nul et que l'on ne retombe pas sur le même lien
                if(anchor_link.startswith("/")): #On le reconsitue si besoin
                    baseURL=URL[:25] #Dans ce site il faut enlever le "/news-analysis/" à la fin de l'URL de base
                    anchor_link=baseURL+anchor_link #Et ensuite le concaténer avec le href
                if (company in a.get('href')) or (company in a.text) or (company.lower() in a.get('href')) or (company.lower() in a.text) \
                or (company.capitalize() in a.get('href')) or (company.capitalize() in a.text):
                    link_found=a.get('href')
                    newpage=requests.get(anchor_link)
                    newsoup=BeautifulSoup(newpage.text, "lxml")
                    article_date=newsoup.find('span', {"class":"pub-date"})['content'] #Ici l'extraction de la date se fait sur la page de l'article
                    article_date=dateparser.parse(article_date).date()
                    article=""
                    for paragraph in newsoup.find_all('p'):
                        article+="\n"+paragraph.text
                    ta=TextAnalyzer(company, article, link_found, article_date) #On crée notre objet analyseur de texte
                    ta.RunAnalysis() #On procède à l'analyse de l'article pour déterminer le statut de cybersécurité de l'entreprise
                    found=True
                    print("Information found on "+anchor_link)
        while(found==False and article_counter<20): #Tant que l'on a pas trouvé ou scrapé moins de 2 pages, on scrape la page suivante. (1 page correspond à 20 articles ici, la premiere page allant de 0 à 20).
            article_counter=article_counter+20
            nextpageURL=URL+"?start="+str(article_counter)
            nextpage=requests.get(nextpageURL)
            if nextpage.ok:
                soup=BeautifulSoup(nextpage.text, "lxml")
                anchors=soup.find_all('a')
                for a in anchors:
                    anchor_link=a.get('href')
                    if(anchor_link != None and a.get('href')!=link_found):
                        if(anchor_link.startswith("/")): #On le reconsitue encore si besoin
                            baseURL=URL[:25]
                            anchor_link=baseURL+anchor_link
                        if (company in a.get('href')) or (company in a.text) or (company.lower() in a.get('href')) or (company.lower() in a.text) \
                        or (company.capitalize() in a.get('href')) or (company.capitalize() in a.text):
                            link_found=a.get('href')
                            newpage=requests.get(anchor_link)
                            newsoup=BeautifulSoup(newpage.text, "lxml")
                            article_date=newsoup.find('span', {"class":"pub-date"})['content']
                            article_date=dateparser.parse(article_date).date()
                            article=""
                            for paragraph in newsoup.find_all('p'):
                                article+="\n"+paragraph.text
                            ta=TextAnalyzer(company, article, link_found, article_date) 
                            ta.RunAnalysis()
                            found=True
                            print("Information found on "+anchor_link)
            else: #Requête page suivante échoue, on sort de la boucle
                print("Request Failure: "+nextpageURL+" returned: "+nextpage)
                break
        if(found==False):
            print("Could not scrape any information about "+ company+" on "+URL)
    else: #L'URL de base est invalide
        print("Request Failure: "+URL+" returned: "+mainpage)

def ScrapeInfosecmag(company):
    URL="https://www.infosecurity-magazine.com/news/"
    found=False
    page_counter=1

    mainpage=requests.get(URL)
    if(mainpage.ok): 
        soup=BeautifulSoup(mainpage.text, "lxml") #On scrape la première page
        anchors=soup.find_all('a')
        link_found=""
        for a in anchors:
            if(a.get('href') != None and a.get('href')!=link_found): #On vérifie que le href n'est pas nul et que l'on ne retombe pas sur le même lien
                if (company in a.get('href')) or (company in a.text) or (company.lower() in a.get('href')) or (company.lower() in a.text) \
                or (company.capitalize() in a.get('href')) or (company.capitalize() in a.text):
                    link_found=a.get('href')
                    newpage=requests.get(a.get('href'))
                    newsoup=BeautifulSoup(newpage.text, "lxml")
                    article_date=a.parent.find('time').text #On extrait la date de l'article qu'il faudra ensuite formatter
                    article_date=dateparser.parse(article_date).date()
                    article=""
                    for paragraph in newsoup.find_all('p'):
                        article+="\n"+paragraph.text
                    ta=TextAnalyzer(company, article, link_found, article_date) #On crée notre objet analyseur de texte
                    ta.RunAnalysis() #On procède à l'analyse de l'article pour déterminer le statut de cybersécurité de l'entreprise
                    found=True
                    print("Information found on "+a.get('href'))
        while(found==False and page_counter<2): #Tant que l'on a pas trouvé ou scrapé moins de 2 pages, on scrape la page suivante.
            nextpageURL=""
            for a in anchors: #Recherche de la page suivante
                anchor=str(a)
                if("rel=\"next\"" in anchor):
                    if(a['href'].startswith("https://")):
                        nextpageURL=a['href']
            if(nextpageURL!=""):
                page_counter=page_counter+1
                nextpage=requests.get(nextpageURL)
                if nextpage.ok:
                    soup=BeautifulSoup(nextpage.text, "lxml")
                    anchors=soup.find_all('a')
                    for a in anchors:
                        if(a.get('href') != None and a.get('href')!=link_found):
                            if (company in a.get('href')) or (company in a.text) or (company.lower() in a.get('href')) or (company.lower() in a.text) \
                            or (company.capitalize() in a.get('href')) or (company.capitalize() in a.text):
                                link_found=a.get('href')
                                newpage=requests.get(a.get('href'))
                                newsoup=BeautifulSoup(newpage.text, "lxml")
                                article_date=a.parent.find('time').text
                                article_date=dateparser.parse(article_date).date()
                                article=""
                                for paragraph in newsoup.find_all('p'):
                                    article+="\n"+paragraph.text
                                found=True
                                ta=TextAnalyzer(company, article, link_found, article_date) 
                                ta.RunAnalysis() 
                                print("Information found on "+a.get('href'))
                else: #Requête page suivante échoue, on sort de la boucle
                    print("Request Failure: "+nextpageURL+" returned: "+nextpage)
                    break
            else: #Pas de page suivante, on sort de la boucle
                break
        if(found==False):
            print("Could not scrape any information about "+ company+" on "+URL)
    else: #L'URL de base est invalide
        print("Request Failure: "+URL+" returned: "+mainpage)

def ScrapeNakedsec(company):
    URL="https://nakedsecurity.sophos.com/"
    found=False
    page_counter=1

    mainpage=requests.get(URL)
    if(mainpage.ok): 
        soup=BeautifulSoup(mainpage.text, "lxml") #On scrape la première page
        anchors=soup.find_all('a')
        link_found=""
        for a in anchors:
            if(a.get('href') != None and a.get('href')!=link_found): #On vérifie que le href n'est pas nul et que l'on ne retombe pas sur le même lien
                if (company in a.get('href')) or (company in a.text) or (company.lower() in a.get('href')) or (company.lower() in a.text) \
                or (company.capitalize() in a.get('href')) or (company.capitalize() in a.text):
                    link_found=a.get('href')
                    newpage=requests.get(a.get('href'))
                    newsoup=BeautifulSoup(newpage.text, "lxml")
                    article_date=newsoup.find('time').text #Ici également, la date s'extrait à partir de la page de l'article
                    article_date=dateparser.parse(article_date).date()
                    article=""
                    for paragraph in newsoup.find_all('p'):
                        article+="\n"+paragraph.text
                    ta=TextAnalyzer(company, article, link_found, article_date) #On crée notre objet analyseur de texte
                    ta.RunAnalysis() #On procède à l'analyse de l'article pour déterminer le statut de cybersécurité de l'entreprise
                    found=True
                    print("Information found on "+a.get('href'))
        while(found==False and page_counter<2): #Tant que l'on a pas trouvé ou scrapé moins de 2 pages, on scrape la page suivante.
            nextpageURL=""
            for a in anchors: #Recherche de la page suivante
                anchor=str(a)
                if("Load more articles" in anchor):
                    if(a['href'].startswith("https://")):
                        nextpageURL=a['href']
            if(nextpageURL!=""):
                page_counter=page_counter+1
                nextpage=requests.get(nextpageURL)
                if nextpage.ok:
                    soup=BeautifulSoup(nextpage.text, "lxml")
                    anchors=soup.find_all('a')
                    for a in anchors:
                        if(a.get('href') != None and a.get('href')!=link_found):
                            if (company in a.get('href')) or (company in a.text) or (company.lower() in a.get('href')) or (company.lower() in a.text) \
                            or (company.capitalize() in a.get('href')) or (company.capitalize() in a.text):
                                link_found=a.get('href')
                                newpage=requests.get(a.get('href'))
                                newsoup=BeautifulSoup(newpage.text, "lxml")
                                article_date=newsoup.find('time').text
                                article_date=dateparser.parse(article_date).date()
                                article=""
                                for paragraph in newsoup.find_all('p'):
                                    article+="\n"+paragraph.text
                                ta=TextAnalyzer(company, article, link_found, article_date) 
                                ta.RunAnalysis() 
                                found=True
                                print("Information found on "+a.get('href'))
                else: #Requête page suivante échoue, on sort de la boucle
                    print("Request Failure: "+nextpageURL+" returned: "+nextpage)
                    break
            else: #Pas de page suivante, on sort de la boucle
                break
        if(found==False):
            print("Could not scrape any information about "+ company+" on "+URL)
    else: #L'URL de base est invalide
        print("Request Failure: "+URL+" returned: "+mainpage)

def ScrapeKebronsec(company):
    URL="https://krebsonsecurity.com/"
    found=False
    page_counter=1

    mainpage=requests.get(URL)
    if(mainpage.ok): 
        soup=BeautifulSoup(mainpage.text, "lxml") #On scrape la première page
        titles=soup.find_all('h2', {"class":"entry-title"})
        link_found=""
        for title in titles:
            a=title.find('a')
            if(a.get('href') != None and a.get('href')!=link_found): #On vérifie que le href n'est pas nul et que l'on ne retombe pas sur le même lien
                if (company in a.get('href')) or (company in a.text) or (company.lower() in a.get('href')) or (company.lower() in a.text) \
                or (company.capitalize() in a.get('href')) or (company.capitalize() in a.text):
                    link_found=a.get('href')
                    newpage=requests.get(a.get('href'))
                    newsoup=BeautifulSoup(newpage.text, "lxml")
                    wrapper=a.parent.parent
                    article_date=wrapper.find('span',{"class":"date updated"}).text #Ici également, la date s'extrait à partir de la page de l'article
                    article_date=dateparser.parse(article_date).date()
                    article=""
                    for paragraph in newsoup.find_all('p'):
                        article+="\n"+paragraph.text
                    ta=TextAnalyzer(company, article, link_found, article_date) #On crée notre objet analyseur de texte
                    ta.RunAnalysis() #On procède à l'analyse de l'article pour déterminer le statut de cybersécurité de l'entreprise
                    print(ta)
                    found=True
                    print("Information found on "+a.get('href'))
        while(found==False and page_counter<2): #Tant que l'on a pas trouvé ou scrapé moins de 2 pages, on scrape la page suivante.
            nextpageURL=""
            for a in anchors: #Recherche de la page suivante
                anchor=str(a)
                if("Next >" in anchor):
                    if(a['href'].startswith("https://")):
                        nextpageURL=a['href']
            if(nextpageURL!=""):
                page_counter=page_counter+1
                nextpage=requests.get(nextpageURL)
                if nextpage.ok:
                    soup=BeautifulSoup(nextpage.text, "lxml")
                    anchors=soup.find_all('a')
                    titles=soup.find_all('h2', {"class":"entry-title"})
                    for title in titles:
                        a=soup.find('a')
                        if(a.get('href') != None and a.get('href')!=link_found):
                            if (company in a.get('href')) or (company in a.text) or (company.lower() in a.get('href')) or (company.lower() in a.text) \
                            or (company.capitalize() in a.get('href')) or (company.capitalize() in a.text):
                                link_found=a.get('href')
                                newpage=requests.get(a.get('href'))
                                newsoup=BeautifulSoup(newpage.text, "lxml")
                                wrapper=a.parent.parent
                                article_date=wrapper.find('span',{"class":"date updated"}).text
                                article_date=dateparser.parse(article_date).date()
                                article=""
                                for paragraph in newsoup.find_all('p'):
                                    article+="\n"+paragraph.text
                                ta=TextAnalyzer(company, article, link_found, article_date) 
                                ta.RunAnalysis() 
                                found=True
                                print("Information found on "+a.get('href'))
                else: #Requête page suivante échoue, on sort de la boucle
                    print("Request Failure: "+nextpageURL+" returned: "+nextpage)
                    break
            else: #Pas de page suivante, on sort de la boucle
                break
        if(found==False):
            print("Could not scrape any information about "+ company+" on "+URL)
    else: #L'URL de base est invalide
        print("Request Failure: "+URL+" returned: "+mainpage)


#-----------------------------------------------------------------------------Twitter-------------------------------------------------------------------------------------------
#Quelques libraries pour scraper Twitter:
#twint ->https://github.com/twintproject/twint/wiki/Configuration (semble ne pas fonctionner)
#twitterscraper -> https://github.com/taspinar/twitterscraper (semble ne pas fonctionner non plus)
#Nous allons utiliser ici l'API standard de twitter (voir "API Twitter.txt") https://developer.twitter.com/en/docs/twitter-api/getting-started/about-twitter-api || https://developer.twitter.com/en/portal/dashboard
#documentation->https://docs.tweepy.org/en/stable/client.html  /!\ Limite de 500k tweets par mois

#Questions:
#Comment sécuriser le code? (ne pas afficher les clés secretes pour l'API)
#Ou procéder à l'analyse de texte?
#Comment ne pas parcourir les mêmes tweets (configurer les paramètres de date correctement)
 
#Crée un client avec les clés de l'API Twitter, pour cela on ouvre le fichier keys.txt qui contient les clés dans l'ordre ci dessous
def getClient():
    with open("keys.txt", "r") as secretfile:
        bearer_token=secretfile.readline().rstrip()
        consumer_key=secretfile.readline().rstrip()
        consumer_secret=secretfile.readline().rstrip()
        access_token=secretfile.readline().rstrip()
        access_token_secret=secretfile.readline().rstrip()
        client=tweepy.Client(bearer_token,consumer_key,consumer_secret,access_token,access_token_secret)
    secretfile.close()
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

#Pour rechercher les tweets d'un utilisateur précis, il faut récupérer son id
def getUserId(username):
    url = 'https://api.twitter.com/2/users/by/username/{}'.format(username)

    with open("keys.txt", "r") as secretfile:
        bearer_token=secretfile.readline().rstrip()
    secretfile.close()
    headers = {'Authorization': 'Bearer {}'.format(bearer_token)}

    #on extrait le profil du user
    response = requests.request('GET', url, headers = headers)
    response = response.json()
    #response = {'data': {'id': '22790881', 'name': 'briankrebs', 'username': 'briankrebs'}}
    id = response['data']['id'] #On récupère l'id dans le dictionnaire response
    
    return id

#test getUserId
#username = 'briankrebs'
#print(getUserId(username)) ->22790881

#Recherche parmi les 10 derniers tweets de l'utilisateur s'il a mentionné l'entreprise recherchée
def SearchTweetsUser2(username, company):
    id = getUserId(username)
    mention = False #Si l'on a trouvé un tweet à propos de l'entreprise

    url = 'https://api.twitter.com/2/users/{}/tweets'.format(id)
    #le bearer_token permet de se connecter à l'API de twitter
    with open("keys.txt", "r") as secretfile:
        bearer_token=secretfile.readline().rstrip()
    secretfile.close()
    headers = {'Authorization': 'Bearer {}'.format(bearer_token)}
    ListAlarmingTweets = []
    response = requests.request('GET', url, headers = headers) #mettre new_url
    tweetsData = response.json()
    for tweetData in tweetsData['data']:
        if(company in tweetData['text']):
            ListAlarmingTweets.append(tweetData)
            mention = True
            #print(tweetData)
                
    return mention, ListAlarmingTweets #On retourne ici un tuple

# Le lien d'un tweet est du style https://twitter.com/<username>/status/<tweet_id>
def SearchTweetsUser(username, company): 
    Client=getClient()
    user_id = getUserId(username)

    result=Client.get_users_tweets(user_id, exclude=['replies'],max_results=5, tweet_fields=['created_at','id','text'])
    #Response(data=[<Tweet id=1481279570322071558 text=A couple of these updates are reportedly causing reboots on domain controllers/ https://t.co/8oSwPp6sfF h/t @campuscodi>, 
    #<Tweet id=1481258396355604487 text="Wazawaka," the handle chosen by a prolific network access broker/ransomware affiliate, has a $5M bounty on his head. “Mother Russia will help you,” Wazawaka concluded. “Love your country, and you will always get away with everything.” https://t.co/1jdNCrgiMh>, 
    #<Tweet id=1481126293601239041 text=@Mitchell10500 No relation to my brother from another mother.>, 
    #<Tweet id=1481030224750026764 text=It's Patch Tuesday, Windows users! Today's batch includes fixes for something like 120 vulnerabilities, including a critical, "wormable" flaw in Windows 10/11 and later Server versions, and 3 Exchange bugs, 1 of which was reported to Microsoft by the NSA. https://t.co/zh1UdM3qZq>, 
    #<Tweet id=1480913660805627913 text=Twitter is prompting me to promote this tweet. For once, I'm intrigued. Treating this as a PSA isn't actually a bad idea.>], 
    #includes={}, errors=[], meta={'oldest_id': '1480913660805627913', 'newest_id': '1481279570322071558', 'result_count': 5, 'next_token': '7140dibdnow9c7btw3z44wd2xpiagw4b026rnpdcajvoz'})
    tweets=result.data
    for tweet in tweets:
        if((company in tweet.text) or (company.lower() in tweet.text) or (company.capitalize() in tweet.text)) or(company.upper() in tweet.text):
            tweet_date=(tweet.created_at).date()
            tweet_link='https://twitter.com/{}/status/{}'.format(username, tweet.id)
            ta=TextAnalyzer(company, tweet.text, tweet_link, tweet_date)
            ta.RunAnalysis()
            yield ta

     

def ScrapeTwitter(company):
    usernames=["briankrebs", "threatpost", "peterkruse"]
    Tweetlist=[]

    for user in usernames:
        for ta in SearchTweetsUser(user, company):
            Tweetlist.append(ta)

    if not Tweetlist:
        print("No information found on twitter about company")
    else:
        for ta in Tweetlist:
            print(ta)
    #{'briankrebs': [<Tweet id=1481030224750026764 text=It's Patch Tuesday, Windows users! Today's batch includes fixes for something like 120 vulnerabilities, including a critical, "wormable" flaw in Windows 10/11 and later Server versions, and 3 Exchange bugs, 1 of which was reported to Microsoft by the NSA. https://t.co/zh1UdM3qZq>], 
    #'threatpost': [<Tweet id=1471484422469955585 text=@Prevailion’s PACT discovered a novel RAT, #DarkWatchman, w/ new #fileless malware techniques, sent in a Russian-language spear-phishing campaign, uniquely manipulating Windows Registry to evade most security detections. #cybersecurity https://t.co/I3HhSiNmSI>], 
    #'peterkruse': []}
      

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def WebScraping(company): 
    ScrapeHackerNews(company)
    ScrapeDarkReading(company) 
    ScrapeZDnet(company)
    ScrapeTechRP(company)
    ScrapeMcAfee(company)
    ScrapeGraham(company)
    ScrapeITsecguru(company) #Ne fonctionne pas encore
    ScrapeCSO(company)
    ScrapeInfosecmag(company)
    ScrapeNakedsec(company)
    ScrapeKebronsec(company)
    #ScrapeTwitter(company) 

def main():
    WebScraping("Samsung")
    
    
    

main()

# PS: Lorsque vous voulez que votre code trouve un élément en particulier de la page, faire un clique droit -> inspecter pour trouver l'élément html correspondant 
# et utiliser soup.find("nom de l'élément"). Pour plus d'infos sur html https://developer.mozilla.org/fr/docs/Web/HTML/Element
# Si vous souhaitez enregistrer du code test sans risquer de détruire le code principal vous pouvez toujours créer une nouvelle branche séparée de la branche main et y téléverser votre code.
# (/!\ Lorsque vous changez de branche et revenez à la branche principale ne les fusionnez pas à moins d'être sûr de la validité du code ajouté!)
