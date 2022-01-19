#Objectif : trier les données des textes après scraping pour ensuite identifier une éventuelle menace/attaque visant une des entreprises partenaire

import numpy as np
import spacy
import pickle
#python -m spacy download en_core_web_md
nlp = spacy.load('en_core_web_md')

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
        par=pickle.load(file)
    file.close()
    return par

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
def TestCountOccurences(text):
    keywords = ['rolled']
    occ = CountOccurences(keywords, text)
    print(occ)


#Retourne un string qui est le sujet de la phrase passée en paramètre
def IdentifySubject(sentence):
    doc = nlp(sentence)
    for token in doc:
        if token.dep_ == 'nsubj':
            return token.text

#Test de la fonction IdentifierSujet
def TestIdentifySubject(text):
    doc = nlp(text)
    first_sentence = list(doc.sents)[0].text
    print("Test sentence : " + first_sentence)
    subject = IdentifySubject(first_sentence)
    print("Subject : " + subject)

def main():
    #print(example_bloc)
    TestIdentifySubject(example_bloc)
    TestCountOccurences(example_bloc)

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