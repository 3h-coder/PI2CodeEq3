#Objectif : trier les données des textes après scraping pour ensuite identifier une éventuelle menace/attaque visant une des entreprises partenaire

import numpy as np
import spacy
#python -m spacy download en_core_web_md
nlp = spacy.load('en_core_web_md')


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

#TestCompteurOccurences()

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

#TestIdentifierSujet()



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