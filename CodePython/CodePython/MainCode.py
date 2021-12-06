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

    sources=["https://thehackernews.com/"] #On part du principe que nos sources sont fiables ici  (les ajouter et tester au fur et à mesure)

    for source in sources:
        #print(source+"\n")
        found=False
        counter=0
        mainpage=requests.get(source)
        soup=BeautifulSoup(mainpage.text, "lxml")
        anchors=soup.find_all('a')
        for a in anchors:
            if (company in a.get('href')) or (company in a.text):
                newpage=requests.get(a.get('href'))
                newsoup=BeautifulSoup(newpage.text, "lxml")
                for paragraph in newsoup.find_all('p'):
                    print(paragraph.text)
                found=True
                #webbrowser.open(a.get('href'))
        while(found==False and counter<5): #Scraper la page suivante tant que l'on a pas trouvé ou scraper moins de 5 pages
            nextpageURL=FindNextPage(soup)
            if(nextpageURL!=""): #On scrape la page suivante
                counter=counter+1
                nextpage=requests.get(nextpageURL)
                webbrowser.open(nextpageURL)
                soup=BeautifulSoup(nextpage.text, "lxml")
                anchors=soup.find_all('a')
                for a in anchors:
                    if (company in a.get('href')) or (company in a.text):
                        newpage=requests.get(a.get('href'))
                        newsoup=BeautifulSoup(newpage.text, "lxml")
                        for paragraph in newsoup.find_all('p'):
                            print(paragraph.text)
                        webbrowser.open(a.get('href'))
                        found=True
            else: #pas de page suivante
                pass
           

        #Questions et pbs: 
        #Jusqu'à où va-t-on scraper?
        #Est-il réaliste de vouloir faire un code général pour une librairie de sources dynamique?
        #La lenteur d'éxecution du programme est problématique
        #Affiner la recherche
           
        #print("\n---------------------------------------------------------------------------------------------------------------------------\n")

def FindNextPage(soup): #Code général pour trouver le lien de la prochaine page (difficile pour plusieurs sources)
    nextURL=""
    anchors=soup.find_all('a')
    for anchor in anchors:
        a=str(anchor)
        if(("Next" in a) or ("next" in a) or ("Page" in a) or ("page" in a) or \
          ("Older" in a) or ("older" in a) ):
            if(anchor['href'].startswith("https://")):
                nextURL=anchor['href']
    return nextURL


def main():
    #print("Hello World!") #Remplacer cette ligne par la fonction à executer.
    webscraping("Ensuring")


main()

#salut
# PS: Lorsque vous voulez que votre code trouve un élément en particulier de la page, faire un clique droit -> inspecter pour trouver l'élément html correspondant 
# et utiliser soup.find("nom de l'élément"). Pour plus d'infos sur html https://developer.mozilla.org/fr/docs/Web/HTML/Element
# Si vous souhaitez enregistrer du code test sans risquer de détruire le code principal vous pouvez toujours créer une nouvelle branche séparée de la branche main et y téléverser votre code.
# (/!\ Lorsque vous changez de branche et revenez à la branche principale ne les fusionnez pas à moins d'être sûr de la validité du code ajouté!)