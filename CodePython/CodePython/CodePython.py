#Le code se fera ici
#regarder un tuto sur git hub / git hub desktop
#installer les librairies nécessaires si non installées (exemple: pip install bs4) 

#On commence par l'exemple de SolarWinds, grande entreprise de contrôle de systèmes informatiques, victime d'une Cyberattaque de grande ampleur en 2020.
#A priori nous aurons déjà nos sources prédéfinies et lorsque que nous nous intéresserons au statut d'une entreprise en particulier,
#nous parcourrons nos sources à l'aide de mots clé (dont le nom de l'entreprise).
#Cependant ici à titre de découverte du web scraping l'approche est un peu différente, nous automatisons le processus de recherche qu'une personne lamba ferait sur Google.
import requests, webbrowser
from bs4 import BeautifulSoup
from googlesearch import search

query= "SolarWinds Cyberattaque" #La recherche que l'on effectue sur Google
links =[] #Liste qui contiendra tous les liens des sites webs que nous allons "scraper" à l'issue de la recherche.

for j in search(query, num=3, stop=3, pause=0.5): #On se contente des 3 résultats jugés les plus pertinents par Google dans cet exemple
    #print(j)
    #webbrowser.open(j)
    links.append(j) #On sauvegarde les liens

for link in links:
    print("-------------------------------------------------------------------------------------------------------------------------------------------------------")
    page=requests.get(link)
    soup=BeautifulSoup(page.text, "lxml")  #Lecture du code source des pages
    print(link+"\n")
    print(soup.find("title").text+"\n") #Titre de la page (à priori un article)
    paragraphes=soup.find_all("p")
    for p in paragraphes:
        print(p.text) #Affichage du contenu rédactionnel de la page


