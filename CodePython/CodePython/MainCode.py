#Do not forget to install from the requirements.txt file before running the program.

from bs4.element import SoupStrainer
import requests, webbrowser
from bs4 import BeautifulSoup
import spacy 
import tweepy
import datetime
import pandas as pd
import dateparser
import warnings
from TextAnalyzer import TextAnalyzer
import TextAnalysis
import string
warnings.filterwarnings("ignore", message="The localize method is no longer necessary, as this time zone supports the fold attribute")

#-----------------------------------------------------------------------------Websites-----------------------------------------------------------------------------------------                
#The goal here is to scrape data from articles. Each website has a 2 scraping functions associated. The first one limits the search to an arbitrary number of pages, while the second will search for 
#information up to a certain date.


def ScrapeHackerNews(company, page_limit=2):
    """
    Searches through the website "thehackernews.com" to return a list of TextAnalyzer objects after running the analysis for each of them as well as printing the analysis result.
    If no information could be found, the function will not return anything.

    Parameters:
    -------------
    company: str
        The company name we are trying to scrape information about.

    page_limit (optional): int
        The maximum number of pages the program will browse, the default value is 2.
    """
    string.capwords(company)
    URL="https://thehackernews.com/"
    found=False
    page_counter=1
    page_limit=int(page_limit)
    
    mainpage=requests.get(URL)
    if(mainpage.ok): 
        soup=BeautifulSoup(mainpage.text, "lxml") #Here we start scraping the first page.
        anchors=soup.find_all('a', {"class": "story-link"})
        link_found="" 
        for a in anchors:
            if(a.get('href') != None and a.get('href')!=link_found): #We make sure that the anchor link is not null and has not been already browsed.
                title=a.find('h2')
                if (company in a.get('href')) or (company in a.text) or (company.lower() in a.get('href')) \
                or (company.capitalize() in a.get('href')) or (company.capitalize() in a.text) \
                or (company.lower() in a.text) or (company in title.text) or (company.lower() in title.text) or (company.capitalize() in title.text): #We "find" something whenever the company name appears in the article content (title included)
                    link_found=a.get('href')
                    article_date=a.find('i', {"class": "icon-font icon-calendar"}).next_sibling #We extract the article date.
                    article_date=dateparser.parse(article_date).date()
                    newpage=requests.get(a.get('href'))
                    newsoup=BeautifulSoup(newpage.text, "lxml")
                    article=""
                    for paragraph in newsoup.find_all('p'): #We extract the article content.
                        article+="\n"+paragraph.text
                    ta=TextAnalyzer(company, article, link_found, article_date)
                    ta.RunAnalysis() #We then proceed to run the analysis to determine whether or not an alert needs to be raised.
                    found=True
                    print("Information found on "+a.get('href')+"   "+ta.result)
                    ta.Save()
        while(page_counter<page_limit): #We keep scraping the next page until the page limit.
            nextpageURL=""
            next_a=soup.find('a', {"class":"blog-pager-older-link-mobile"}) #Here we search for the next page link.
            if(next_a!=None and next_a['href'].startswith("https://")):
                        nextpageURL=next_a['href']
            if(nextpageURL!=""):
                page_counter=page_counter+1
                nextpage=requests.get(nextpageURL)
                if nextpage.ok:
                    soup=BeautifulSoup(nextpage.text, "lxml")  #Here we start scraping the next page.
                    anchors=soup.find_all('a', {"class": "story-link"})
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
                                print("Information found on "+a.get('href')+"   "+ta.result)
                                ta.Save()
                else: #We could not access the next page.
                    print("Request Failure: "+nextpageURL+" returned: "+str(nextpage))
                    break
            else: #We could not find the next page.
                break
        if(found==False):
            print("Could not scrape any information about "+ company+" on "+URL)
    else: #We could not access the website.
        print("Request Failure: "+URL+" returned: "+str(mainpage))

def ScrapeHackerNews2(company, date):
    """
    Searches through the website "thehackernews.com" to return a list of TextAnalyzer objects after running the analysis for each of them as well as printing the analysis result.
    If no information could be found, the function will not return anything.

    Parameters:
    -------------
    company: str
        The company name we are trying to scrape information about.

    date: date
        The date until which we scrape information. We do not search any information that is anterior to it.
    """
    string.capwords(company)
    URL="https://thehackernews.com/"
    found=False

    mainpage=requests.get(URL)
    if(mainpage.ok):
        soup=BeautifulSoup(mainpage.text, "lxml") #Here we start scraping the first page.
        anchors=soup.find_all('a', {"class": "story-link"})
        link_found=""
        last_article_date=""
        for a in anchors:
            if(a.get('href') != None and a.get('href')!=link_found): #We make sure that the anchor link is not null and has not been already browsed.
                article_date=a.find('i', {"class": "icon-font icon-calendar"}).next_sibling #We extract the article date first.
                article_date=dateparser.parse(article_date).date()
                last_article_date=article_date
                if(article_date < date): #We check whether the article date is anterior to our input date or not. If it is, we exit the function.
                    if(found==False):
                        print("Could not find any information about "+company+" on "+URL)
                        return
                    else:
                        return
                title=a.find('h2')
                if (company in a.get('href')) or (company in a.text) or (company.lower() in a.get('href')) \
                or (company.capitalize() in a.get('href')) or (company.capitalize() in a.text) \
                or (company.lower() in a.text) or (company in title.text) or (company.lower() in title.text) or (company.capitalize() in title.text): #We "find" something whenever the company name appears in the article content (title included)
                    link_found=a.get('href')
                    newpage=requests.get(a.get('href'))
                    newsoup=BeautifulSoup(newpage.text, "lxml")
                    article=""
                    for paragraph in newsoup.find_all('p'): #We extract the article content.
                        article+="\n"+paragraph.text
                    ta=TextAnalyzer(company, article, link_found, article_date) 
                    ta.RunAnalysis() #We then proceed to run the analysis to determine whether or not an alert needs to be raised.
                    found=True
                    print("Information found on "+a.get('href')+"   "+ta.result)
                    ta.Save()
        while(last_article_date > date): #We keep scraping the next page until we reach our date.
            nextpageURL=""
            next_a=soup.find('a', {"class":"blog-pager-older-link-mobile"}) #Here we search for the next page link.
            if(next_a!=None and next_a['href'].startswith("https://")): 
                        nextpageURL=next_a['href']
            if(nextpageURL!=""):
                nextpage=requests.get(nextpageURL)
                if(nextpage.ok):
                    soup=BeautifulSoup(nextpage.text, "lxml") #Here we start scraping the next page.
                    anchors=soup.find_all('a',{"class": "story-link"})
                    for a in anchors:
                        if(a.get('href') != None and a.get('href')!=link_found):
                            article_date=a.find('i', {"class": "icon-font icon-calendar"}).next_sibling 
                            article_date=dateparser.parse(article_date).date()
                            last_article_date=article_date
                            if(article_date < date):
                                if(found==False):
                                    print("Could not find any information about "+company+" on "+URL)
                                    return
                                else:
                                    return
                            title=a.find('h2')
                            if (company in a.get('href')) or (company in a.text) or (company.lower() in a.get('href')) \
                                or (company.capitalize() in a.get('href')) or (company.capitalize() in a.text) \
                                or (company.lower() in a.text) or (company in title.text) or (company.lower() in title.text) or (company.capitalize() in title.text):
                                link_found=a.get('href')
                                newpage=requests.get(a.get('href'))
                                newsoup=BeautifulSoup(newpage.text, "lxml")
                                article=""
                                for paragraph in newsoup.find_all('p'):
                                    article+="\n"+paragraph.text
                                ta=TextAnalyzer(company, article, link_found, article_date) 
                                ta.RunAnalysis()
                                found=True
                                print("Information found on "+a.get('href')+"   "+ta.result)
                                ta.Save()
                else: #We could not access the next page.
                    print("Request Failure: "+nextpageURL+" returned: "+str(nextpage))
                    break
            else: #We could not find the next page.
                break
        if(found==False):
                print("Could not scrape any information about "+ company+" on "+URL)
    else: #We could not access the website.
        print("Request Failure: "+URL+" returned: "+str(mainpage))

def ScrapeDarkReading(company, page_limit=2): #Infinite scroll website
    """
    Searches through the website "darkreading.com/attacks-breaches" to return a list of TextAnalyzer objects after running the analysis for each of them as well as printing the analysis result.
    If no information could be found, the function will not return anything.

    Parameters:
    -------------
    company: str
        The company name we are trying to scrape information about.

    page_limit (optional): int
        The maximum number of pages the program will browse, the default value is 2.
    """
    string.capwords(company)
    URL="https://www.darkreading.com/attacks-breaches"
    found=False
    page_counter=1
    page_limit=int(page_limit)

    mainpage=requests.get(URL)
    if(mainpage.ok): 
        soup=BeautifulSoup(mainpage.text, "lxml") 
        anchors=soup.find_all('a', {"class":"article-title"})
        link_found=""
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
                    print("Information found on "+a.get('href')+"   "+ta.result)
                    ta.Save()
        while(page_counter<2):
            page_counter=page_counter+1
            nextpageURL="https://www.darkreading.com/attacks-breaches?page={}".format(page_counter)
            if(nextpageURL!=""):
                nextpage=requests.get(nextpageURL)
                if nextpage.ok:
                    soup=BeautifulSoup(nextpage.text, "lxml")
                    anchors=soup.find_all('a',{"class":"article-title"})
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
                                print("Information found on "+a.get('href')+"   "+ta.result)
                                ta.Save()
                else: 
                    print("Request Failure: "+nextpageURL+" returned: "+str(nextpage))
                    break
            else: 
                break
        if(found==False):
            print("Could not scrape any information about "+ company+" on "+URL)
    else: 
        print("Request Failure: "+URL+" returned: "+str(mainpage))

def ScrapeDarkReading2(company, date):
    """
    Searches through the website "darkreading.com/attacks-breaches" to return a list of TextAnalyzer objects after running the analysis for each of them as well as printing the analysis result.
    If no information could be found, the function will not return anything.

    Parameters:
    -------------
    company: str
        The company name we are trying to scrape information about.

    date: date
        The date until which we scrape information. We do not search any information that is anterior to it.
    """
    string.capwords(company)
    URL="https://www.darkreading.com/attacks-breaches"
    found=False
    page_counter=1

    mainpage=requests.get(URL)
    if(mainpage.ok): 
        soup=BeautifulSoup(mainpage.text, "lxml") 
        anchors=soup.find_all('a',{"class":"article-title"})
        link_found=""
        last_article_date=""
        for a in anchors:
            if(a.get('href') != None and a.get('href')!=link_found): 
                wrapper=a.parent.parent
                article_date=(wrapper.find("div", {"class": "d-md-none arcile-date"}).text) 
                article_date=dateparser.parse(article_date).date()
                last_article_date=article_date
                if(article_date < date): 
                    if(found==False):
                        print("Could not find any information about "+company+" on "+URL)
                        return
                    else:
                        return
                if (company in a.get('href')) or (company in a.text) or (company.lower() in a.get('href')) or (company.lower() in a.text) \
                or (company.capitalize() in a.get('href')) or (company.capitalize() in a.text):
                    link_found=a.get('href')
                    newpage=requests.get(a.get('href'))
                    newsoup=BeautifulSoup(newpage.text, "lxml")
                    article=""
                    for paragraph in newsoup.find_all('p'):
                        article+="\n"+paragraph.text
                    ta=TextAnalyzer(company, article, link_found, article_date) 
                    ta.RunAnalysis() 
                    found=True
                    print("Information found on "+a.get('href')+"   "+ta.result)
                    ta.Save()
        while(last_article_date > date):
            page_counter=page_counter+1
            nextpageURL="https://www.darkreading.com/attacks-breaches?page={}".format(page_counter)
            if(nextpageURL!=""):
                nextpage=requests.get(nextpageURL)
                if nextpage.ok:
                    soup=BeautifulSoup(nextpage.text, "lxml")
                    anchors=soup.find_all('a',{"class":"article-title"})
                    for a in anchors:
                        if(a.get('href') != None and a.get('href')!=link_found):
                            wrapper=a.parent.parent
                            article_date=(wrapper.find("div", {"class": "d-md-none arcile-date"}).text) 
                            article_date=dateparser.parse(article_date).date()
                            last_article_date=article_date
                            if(article_date < date): 
                                if(found==False):
                                    print("Could not find any information about "+company+" on "+URL)
                                    return
                                else:
                                    return
                            if (company in a.get('href')) or (company in a.text) or (company.lower() in a.get('href')) or (company.lower() in a.text) \
                            or (company.capitalize() in a.get('href')) or (company.capitalize() in a.text):
                                link_found=a.get('href')
                                newpage=requests.get(a.get('href'))
                                newsoup=BeautifulSoup(newpage.text, "lxml")
                                article=""
                                for paragraph in newsoup.find_all('p'):
                                    article+="\n"+paragraph.text
                                ta=TextAnalyzer(company, article, link_found, article_date) 
                                ta.RunAnalysis() 
                                found=True
                                print("Information found on "+a.get('href')+"   "+ta.result)
                                ta.Save()
                else: 
                    print("Request Failure: "+nextpageURL+" returned: "+str(nextpage))
                    break
            else: 
                break
        if(found==False):
            print("Could not scrape any information about "+ company+" on "+URL)
    else: 
        print("Request Failure: "+URL+" returned: "+str(mainpage))

def ScrapeZDnet(company, page_limit=2): #URL rebuilding necessary  --> stringObject[start:stop:interval]
    """
    Searches through the website "zdnet.com/blog/security" to return a list of TextAnalyzer objects after running the analysis for each of them as well as printing the analysis result.
    If no information could be found, the function will not return anything.

    Parameters:
    -------------
    company: str
        The company name we are trying to scrape information about.

    page_limit (optional): int
        The maximum number of pages the program will browse, the default value is 2.
    """
    string.capwords(company)
    URL="https://www.zdnet.com/blog/security/"
    found=False
    page_counter=1
    page_limit=int(page_limit)

    mainpage=requests.get(URL)
    if(mainpage.ok): 
        soup=BeautifulSoup(mainpage.text, "lxml") 
        anchors=soup.find_all('a', {"class":"thumb"})
        link_found=""
        for a in anchors:
            anchor_link=a.get('href')
            if(a.get('href') != None and a.get('href')!=link_found): 
                if(anchor_link.startswith("/")): #We rebuild the URL
                    anchor_link=anchor_link[1:] #Remove the "/" at the beginning
                    anchor_link=URL+anchor_link #Concatenate it with the base URL
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
                    print("Information found on "+anchor_link+"   "+ta.result)
                    ta.Save()
        while(page_counter<page_limit): 
            nextpageURL=""
            next_a=soup.find('a', {"class":"next"})
            if next_a!=None and (next_a['href'].startswith("https://")):
                nextpageURL=next_a['href']
            if(nextpageURL!=""):
                print(nextpageURL)
                page_counter=page_counter+1
                nextpage=requests.get(nextpageURL)
                if nextpage.ok:
                    soup=BeautifulSoup(nextpage.text, "lxml")
                    anchors=soup.find_all('a', {"class":"thumb"})
                    for a in anchors[:15]:
                        anchor_link=a.get('href')
                        if(anchor_link != None and a.get('href')!=link_found):
                            if(anchor_link.startswith("/")): #We rebuild it again
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
                                print("Information found on "+anchor_link+"   "+ta.result)
                                ta.Save()
                else: 
                    print("Request Failure: "+nextpageURL+" returned: "+str(nextpage))
                    break
            else: 
                break
        if(found==False):
            print("Could not scrape any information about "+ company+" on "+URL)
    else: 
        print("Request Failure: "+URL+" returned: "+str(mainpage))

def ScrapeZDnet2(company, date):
    """
    Searches through the website "zdnet.com/blog/security" to return a list of TextAnalyzer objects after running the analysis for each of them as well as printing the analysis result.
    If no information could be found, the function will not return anything.

    Parameters:
    -------------
    company: str
        The company name we are trying to scrape information about.

    date: date
        The date until which we scrape information. We do not search any information that is anterior to it.
    """
    string.capwords(company)
    URL="https://www.zdnet.com/blog/security/"
    found=False

    mainpage=requests.get(URL)
    if(mainpage.ok): 
        soup=BeautifulSoup(mainpage.text, "lxml") 
        anchors=soup.find_all('a', {"class":"thumb"})
        link_found=""
        last_article_date=""
        for a in anchors[:15]: #We only take into account the first 15 articles of the page here (the others are irrelevant).
            anchor_link=a.get('href')
            if(a.get('href') != None and a.get('href')!=link_found): 
                if(anchor_link.startswith("/")): 
                    anchor_link=anchor_link[1:] 
                    anchor_link=URL+anchor_link 
                    wrapper=a.parent.parent
                    article_date=wrapper.find('p', {"class":"meta"}).find('span')['data-date'] 
                    article_date=dateparser.parse(article_date).date()
                    last_article_date=article_date
                    if(article_date < date): 
                        if(found==False):
                            print("Could not find any information about "+company+" on "+URL)
                            return
                        else:
                            return
                if (company in a.get('href')) or (company in a.text) or (company.lower() in a.get('href')) or (company.lower() in a.text) \
                or (company.capitalize() in a.get('href')) or (company.capitalize() in a.text):
                    link_found=a.get('href')
                    newpage=requests.get(anchor_link)
                    newsoup=BeautifulSoup(newpage.text, "lxml")
                    article=""
                    for paragraph in newsoup.find_all('p'):
                        article+="\n"+paragraph.text
                    ta=TextAnalyzer(company, article, link_found, article_date) 
                    ta.RunAnalysis() 
                    found=True
                    print("Information found on "+anchor_link+"   "+ta.result)
                    ta.Save()
        while(last_article_date > date): 
            nextpageURL=""
            next_a=soup.find('a', {"class":"next"})
            if next_a!=None and (next_a['href'].startswith("https://")):
                nextpageURL=next_a['href']
            if(nextpageURL!=""):
                nextpage=requests.get(nextpageURL)
                if nextpage.ok:
                    soup=BeautifulSoup(nextpage.text, "lxml")
                    anchors=soup.find_all('a', {"class":"thumb"})
                    for a in anchors[:15]:
                        anchor_link=a.get('href')
                        if(anchor_link != None and a.get('href')!=link_found):
                            if(anchor_link.startswith("/")): 
                                anchor_link=anchor_link[1:]
                                anchor_link=URL+anchor_link
                                wrapper=a.parent.parent
                                article_date=wrapper.find('p', {"class":"meta"}).find('span')['data-date'] 
                                article_date=dateparser.parse(article_date).date()
                                last_article_date=article_date
                                if(article_date < date): 
                                    if(found==False):
                                        print("Could not find any information about "+company+" on "+URL)
                                        return
                                    else:
                                        return
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
                                print("Information found on "+anchor_link+"   "+ta.result)
                                ta.Save()
                else: 
                    print("Request Failure: "+nextpageURL+" returned: "+str(nextpage))
                    break
            else: 
                break
        if(found==False):
            print("Could not scrape any information about "+ company+" on "+URL)
    else: 
        print("Request Failure: "+URL+" returned: "+str(mainpage))

def ScrapeTechRP(company, page_limit=2):
    """
    Searches through the website "techrepublic.com/topic/security" to return a list of TextAnalyzer objects after running the analysis for each of them as well as printing the analysis result.
    If no information could be found, the function will not return anything.

    Parameters:
    -------------
    company: str
        The company name we are trying to scrape information about.

    page_limit (optional): int
        The maximum number of pages the program will browse, the default value is 2.
    """
    string.capwords(company)
    URL="https://www.techrepublic.com/topic/security/"
    found=False
    page_counter=1
    page_limit=int(page_limit)
    
    mainpage=requests.get(URL)
    if(mainpage.ok): 
        soup=BeautifulSoup(mainpage.text, "lxml") 
        anchors=soup.find_all('a')
        link_found="" 
        for a in anchors:
            if(a.get('href') != None and a.get('href')!=link_found and not a.get('href').startswith("https://www.techrepublic.com/resource-library")): 
                if (company in a.get('href')) or (company in a.text) or (company.lower() in a.get('href')) or (company.lower() in a.text) \
                or (company.capitalize() in a.get('href')) or (company.capitalize() in a.text):
                    link_found=a.get('href')
                    newpage=requests.get(a.get('href'))
                    newsoup=BeautifulSoup(newpage.text, "lxml")
                    wrapper=a.find_parent('article')
                    span=wrapper.find('span',{"class":"date-published"})
                    article_date=span.find('time').text 
                    article_date=dateparser.parse(article_date).date()
                    article=""
                    for paragraph in newsoup.find_all('p'):
                        article+="\n"+paragraph.text
                    ta=TextAnalyzer(company, article, link_found, article_date) 
                    ta.RunAnalysis() 
                    found=True
                    print("Information found on "+a.get('href')+"   "+ta.result)
                    ta.Save()
        while(page_counter<page_limit): 
            nextpageURL=""
            next_a=soup.find('a', {"class":"next page-numbers"})
            if(next_a!=None and next_a.get('href').startswith("https://")):
                nextpageURL=next_a['href']
            if(nextpageURL!=""):
                page_counter=page_counter+1
                nextpage=requests.get(nextpageURL)
                if nextpage.ok:
                    soup=BeautifulSoup(nextpage.text, "lxml")
                    anchors=soup.find_all('a')
                    for a in anchors:
                        if(a.get('href') != None and a.get('href')!=link_found and not a.get('href').startswith("https://www.techrepublic.com/resource-library")):
                            if (company in a.get('href')) or (company in a.text) or (company.lower() in a.get('href')) or (company.lower() in a.text) \
                            or (company.capitalize() in a.get('href')) or (company.capitalize() in a.text):
                                link_found=a.get('href')
                                newpage=requests.get(a.get('href'))
                                newsoup=BeautifulSoup(newpage.text, "lxml")
                                wrapper=a.find_parent('article')
                                span=wrapper.find('span',{"class":"date-published"})
                                article_date=span.find('time').text 
                                article_date=dateparser.parse(article_date).date()
                                article=""
                                for paragraph in newsoup.find_all('p'):
                                    article+="\n"+paragraph.text
                                ta=TextAnalyzer(company, article, link_found, article_date) 
                                ta.RunAnalysis() 
                                found=True
                                print("Information found on "+a.get('href')+"   "+ta.result)
                                ta.Save()
                else: 
                    print("Request Failure: "+nextpageURL+" returned: "+str(nextpage))
                    break
            else: 
                break
        if(found==False):
            print("Could not scrape any information about "+ company+" on "+URL)
    else: 
        print("Request Failure: "+URL+" returned: "+str(mainpage))

def ScrapeTechRP2(company, date):
    """
    Searches through the website "techrepublic.com/topic/security" to return a list of TextAnalyzer objects after running the analysis for each of them as well as printing the analysis result.
    If no information could be found, the function will not return anything.

    Parameters:
    -------------
    company: str
        The company name we are trying to scrape information about.

    date: date
        The date until which we scrape information. We do not search any information that is anterior to it.
    """
    string.capwords(company)
    URL="https://www.techrepublic.com/topic/security/"
    found=False

    mainpage=requests.get(URL)
    if(mainpage.ok): 
        soup=BeautifulSoup(mainpage.text, "lxml") 
        articles=soup.find_all('article')
        link_found="" 
        last_article_date=""
        for article in articles:
            anchors=article.find_all('a')
            for a in anchors:
                if(a.get('href') != None and a.get('href')!=link_found and not a.get('href').startswith("https://www.techrepublic.com/resource-library")): 
                    wrapper=a.find_parent('article')
                    try:
                        span=wrapper.find('span',{"class":"date-published"})
                        article_date=span.find('time').text 
                        article_date=dateparser.parse(article_date).date()
                        last_article_date=article_date
                        if(article_date < date): 
                            if(found==False):
                                print("Could not find any information about "+company+" on "+URL)
                                return
                            else:
                                return
                        if (company in a.get('href')) or (company in a.text) or (company.lower() in a.get('href')) or (company.lower() in a.text) \
                        or (company.capitalize() in a.get('href')) or (company.capitalize() in a.text):
                            link_found=a.get('href')
                            newpage=requests.get(a.get('href'))
                            newsoup=BeautifulSoup(newpage.text, "lxml")
                            article=""
                            for paragraph in newsoup.find_all('p'):
                                article+="\n"+paragraph.text
                            ta=TextAnalyzer(company, article, link_found, article_date) 
                            ta.RunAnalysis() 
                            found=True
                            print("Information found on "+a.get('href')+"   "+ta.result)
                            ta.Save()
                    except:
                       pass
        while(last_article_date > date): 
            nextpageURL=""
            next_a=soup.find('a', {"class":"next page-numbers"})
            if(next_a!=None and next_a.get('href').startswith("https://")):
                nextpageURL=next_a['href']
            if(nextpageURL!=""):
                nextpage=requests.get(nextpageURL)
                if nextpage.ok:
                    soup=BeautifulSoup(nextpage.text, "lxml")
                    articles=soup.find_all('article')
                    for article in articles:
                        anchors=article.find_all('a')
                        for a in anchors:
                            if(a.get('href') != None and a.get('href')!=link_found and not a.get('href').startswith("https://www.techrepublic.com/resource-library")):
                                wrapper=a.find_parent('article')
                                try:
                                    span=wrapper.find('span',{"class":"date-published"})
                                    article_date=span.find('time').text 
                                    article_date=dateparser.parse(article_date).date()
                                    last_article_date=article_date
                                    if(article_date < date): 
                                        if(found==False):
                                            print("Could not find any information about "+company+" on "+URL)
                                            return
                                        else:
                                            return
                                    if (company in a.get('href')) or (company in a.text) or (company.lower() in a.get('href')) or (company.lower() in a.text) \
                                    or (company.capitalize() in a.get('href')) or (company.capitalize() in a.text):
                                        link_found=a.get('href')
                                        newpage=requests.get(a.get('href'))
                                        newsoup=BeautifulSoup(newpage.text, "lxml")
                                        article=""
                                        for paragraph in newsoup.find_all('p'):
                                            article+="\n"+paragraph.text
                                        ta=TextAnalyzer(company, article, link_found, article_date) 
                                        ta.RunAnalysis() 
                                        found=True
                                        print("Information found on "+a.get('href')+"   "+ta.result)
                                        ta.Save()
                                except:
                                    pass
                else: 
                    print("Request Failure: "+nextpageURL+" returned: "+str(nextpage))
                    break
            else: 
                break
        if(found==False):
            print("Could not scrape any information about "+ company+" on "+URL)
    else: 
        print("Request Failure: "+URL+" returned: "+str(mainpage))

def ScrapeMcAfee(company, page_limit=2):
    """
    Searches through the website "mcafee.com/blogs/other-blogs/mcafee-labs" to return a list of TextAnalyzer objects after running the analysis for each of them as well as printing the analysis result.
    If no information could be found, the function will not return anything.

    Parameters:
    -------------
    company: str
        The company name we are trying to scrape information about.

    page_limit (optional): int
        The maximum number of pages the program will browse, the default value is 2.
    """
    string.capwords(company)
    URL="https://www.mcafee.com/blogs/other-blogs/mcafee-labs/"
    found=False
    page_counter=1
    page_limit=int(page_limit)

    mainpage=requests.get(URL)
    if(mainpage.ok): 
        soup=BeautifulSoup(mainpage.text, "lxml") 
        anchors=soup.find_all('a')
        link_found=""
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
                    print("Information found on "+a.get('href')+"   "+ta.result)
                    ta.Save()
        while(page_counter<page_limit): 
            nextpageURL=""
            next_a=soup.find('a', {"class":"next page-numbers"})
            if(next_a!=None and next_a.get('href').startswith("https://")):
                nextpageURL=next_a['href']
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
                                print("Information found on "+a.get('href')+"   "+ta.result)
                                ta.Save()
                else: 
                    print("Request Failure: "+nextpageURL+" returned: "+nextpage)
                    break
            else:
                break
        if(found==False):
            print("Could not scrape any information about "+ company+" on "+URL)
    else: 
        print("Request Failure: "+URL+" returned: "+mainpage)

def ScrapeMcAfee2(company, date):
    """
    Searches through the website "mcafee.com/blogs/other-blogs/mcafee-labs" to return a list of TextAnalyzer objects after running the analysis for each of them as well as printing the analysis result.
    If no information could be found, the function will not return anything.

    Parameters:
    -------------
    company: str
        The company name we are trying to scrape information about.

    date: date
        The date until which we scrape information. We do not search any information that is anterior to it.
    """
    string.capwords(company)
    URL="https://www.mcafee.com/blogs/other-blogs/mcafee-labs/"
    found=False

    mainpage=requests.get(URL)
    if(mainpage.ok): 
        soup=BeautifulSoup(mainpage.text, "lxml") #On scrape la première page
        divs=soup.find_all('div', {"class":"card"})
        link_found=""
        last_article_date=""
        for div in divs:
            try:
                article_date=div.find('small', {"class":"text-muted"}).text
                article_date=dateparser.parse(article_date).date()
                last_article_date=article_date
                if(article_date < date): 
                    if(found==False):
                        print("Could not find any information about "+company+" on "+URL)
                        return
                    else:
                        return
                anchors=div.find_all('a')
                for a in anchors:
                    if(a.get('href') != None and a.get('href')!=link_found): 
                        if (company in a.get('href')) or (company in a.text) or (company.lower() in a.get('href')) or (company.lower() in a.text) \
                        or (company.capitalize() in a.get('href')) or (company.capitalize() in a.text):
                            link_found=a.get('href')
                            newpage=requests.get(a.get('href'))
                            newsoup=BeautifulSoup(newpage.text, "lxml")
                            article=""
                            for paragraph in newsoup.find_all('p'):
                                article+="\n"+paragraph.text
                            ta=TextAnalyzer(company, article, link_found, article_date) 
                            ta.RunAnalysis() 
                            found=True
                            print("Information found on "+a.get('href')+"   "+ta.result)
                            ta.Save()
            except:
                pass
        while(last_article_date > date): 
            nextpageURL=""
            next_a=soup.find('a', {"class":"next page-numbers"})
            if(next_a!=None and next_a.get('href').startswith("https://")):
                nextpageURL=next_a['href']
            if(nextpageURL!=""):
                nextpage=requests.get(nextpageURL)
                if nextpage.ok:
                    soup=BeautifulSoup(nextpage.text, "lxml")
                    divs=soup.find_all('div',{"class":"card"})
                    for div in divs:
                        try:
                            article_date=div.find('small', {"class":"text-muted"}).text
                            article_date=dateparser.parse(article_date).date()
                            last_article_date=article_date
                            if(article_date < date): 
                                if(found==False):
                                    print("Could not find any information about "+company+" on "+URL)
                                    return
                                else:
                                    return
                            anchors=div.find_all('a')
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
                                        print("Information found on "+a.get('href')+"   "+ta.result)
                                        ta.Save()
                        except:
                            pass
                else: 
                    print("Request Failure: "+nextpageURL+" returned: "+nextpage)
                    break
            else: 
                break
        if(found==False):
            print("Could not scrape any information about "+ company+" on "+URL)
    else: 
        print("Request Failure: "+URL+" returned: "+mainpage)

def ScrapeGraham(company, page_limit=2): #Necessary headers assignment, otherwise 403 response
    """
    Searches through the website "grahamcluley.com" to return a list of TextAnalyzer objects after running the analysis for each of them as well as printing the analysis result.
    If no information could be found, the function will not return anything.

    Parameters:
    -------------
    company: str
        The company name we are trying to scrape information about.

    page_limit (optional): int
        The maximum number of pages the program will browse, the default value is 2.
    """
    string.capwords(company)
    URL="https://grahamcluley.com/"
    found=False
    page_counter=1
    headers={"User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"}
    page_limit=int(page_limit)

    mainpage=requests.get(URL, headers=headers)
    if(mainpage.ok): 
        soup=BeautifulSoup(mainpage.text, "lxml") 
        anchors=soup.find_all('a')
        link_found=""
        for a in anchors:
            if(a.get('href') != None and a.get('href')!=link_found): 
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
                    print("Information found on "+a.get('href')+"   "+ta.result)
                    ta.Save()
        while(page_counter<page_limit): 
            nextpageURL=""
            next_a=soup.find('a', {"class":"nextpostslink"})
            if(next_a!=None and next_a.get('href').startswith("https://")):
                nextpageURL=next_a['href']
            if(nextpageURL!=""):
                page_counter=page_counter+1
                nextpage=requests.get(nextpageURL, headers=headers)
                if nextpage.ok:
                    soup=BeautifulSoup(nextpage.text, "lxml")
                    anchors=soup.find_all('a')
                    for a in anchors:
                        if(a.get('href') != None and a.get('href')!=link_found):
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
                                print("Information found on "+a.get('href')+"   "+ta.result)
                                ta.Save()
                else: 
                    print("Request Failure: "+nextpageURL+" returned: "+str(nextpage))
                    break
            else: 
                break
        if(found==False):
            print("Could not scrape any information about "+ company+" on "+URL)
    else: 
        print("Request Failure: "+URL+" returned: "+str(mainpage))

def ScrapeGraham2(company, date):
    """
    Searches through the website "grahamcluley.com" to return a list of TextAnalyzer objects after running the analysis for each of them as well as printing the analysis result.
    If no information could be found, the function will not return anything.

    Parameters:
    -------------
    company: str
        The company name we are trying to scrape information about.

    date: date
        The date until which we scrape information. We do not search any information that is anterior to it.
    """
    string.capwords(company)
    URL="https://grahamcluley.com/"
    found=False
    headers={"User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"}

    mainpage=requests.get(URL, headers=headers)
    if(mainpage.ok): 
        soup=BeautifulSoup(mainpage.text, "lxml") 
        articles=soup.find_all('article')
        link_found=""
        last_article_date=""
        for article in articles:
            article_date=article.find('span', {"class":"post-date"}).text 
            article_date=dateparser.parse(article_date).date()
            last_article_date=article_date
            if(article_date < date): 
                    if(found==False):
                        print("Could not find any information about "+company+" on "+URL)
                        return
                    else:
                        return
            anchors=article.find_all('a')
            for a in anchors:
                if(a.get('href') != None and a.get('href')!=link_found): 
                    if (company in a.get('href')) or (company in a.text) or (company.lower() in a.get('href')) or (company.lower() in a.text) \
                    or (company.capitalize() in a.get('href')) or (company.capitalize() in a.text):
                        link_found=a.get('href')
                        newpage=requests.get(a.get('href'), headers=headers)
                        newsoup=BeautifulSoup(newpage.text, "lxml")              
                        article=""
                        for paragraph in newsoup.find_all('p'):
                            article+="\n"+paragraph.text
                        ta=TextAnalyzer(company, article, link_found, article_date) 
                        ta.RunAnalysis() 
                        found=True
                        print("Information found on "+a.get('href')+"   "+ta.result)
                        ta.Save()
        while(last_article_date > date): 
            nextpageURL=""
            next_a=soup.find('a', {"class":"nextpostslink"})
            if(next_a!=None and next_a.get('href').startswith("https://")):
                nextpageURL=next_a['href']
            if(nextpageURL!=""):
                nextpage=requests.get(nextpageURL, headers=headers)
                if nextpage.ok:
                    soup=BeautifulSoup(nextpage.text, "lxml")
                    articles=soup.find_all('article')
                    for article in articles:
                        article_date=article.find('span', {"class":"post-date"}).text 
                        article_date=dateparser.parse(article_date).date()
                        last_article_date=article_date
                        if(article_date < date): 
                            if(found==False):
                                print("Could not find any information about "+company+" on "+URL)
                                return
                            else:
                                return
                        anchors=soup.find_all('a')
                        for a in anchors:
                            if(a.get('href') != None and a.get('href')!=link_found):
                                if (company in a.get('href')) or (company in a.text) or (company.lower() in a.get('href')) or (company.lower() in a.text) \
                                or (company.capitalize() in a.get('href')) or (company.capitalize() in a.text):
                                    link_found=a.get('href')
                                    newpage=requests.get(a.get('href'), headers=headers)
                                    newsoup=BeautifulSoup(newpage.text, "lxml")
                                    article=""
                                    for paragraph in newsoup.find_all('p'):
                                        article+="\n"+paragraph.text
                                    ta=TextAnalyzer(company, article, link_found, article_date) 
                                    ta.RunAnalysis() 
                                    found=True
                                    print("Information found on "+a.get('href')+"   "+ta.result)
                                    ta.Save()
                else: 
                    print("Request Failure: "+nextpageURL+" returned: "+str(nextpage))
                    break
            else: 
                break
        if(found==False):
            print("Could not scrape any information about "+ company+" on "+URL)
    else: 
        print("Request Failure: "+URL+" returned: "+str(mainpage))

def ScrapeITsecguru(company): #Infinite scroll, not done yet
    URL="https://www.itsecurityguru.org/news/"
    print("Nothing for now.")

def ScrapeCSO(company, page_limit=2): #Necessary URL rebuilding 
    """
    Searches through the website "csoonline.com/news-analysis" to return a list of TextAnalyzer objects after running the analysis for each of them as well as printing the analysis result.
    If no information could be found, the function will not return anything.

    Parameters:
    -------------
    company: str
        The company name we are trying to scrape information about.

    page_limit (optional): int
        The maximum number of pages the program will browse, the default value is 2.
    """
    string.capwords(company)
    URL="https://www.csoonline.com/news-analysis/"
    found=False
    page_limit=int(page_limit)
    article_counter=0
    article_limit=page_limit*20 #One page is equivalent to 20 articles on this website

    mainpage=requests.get(URL)
    if(mainpage.ok): 
        soup=BeautifulSoup(mainpage.text, "lxml") 
        anchors=soup.find_all('a')
        link_found=""
        for a in anchors:
            anchor_link=a.get('href')
            if(a.get('href') != None and a.get('href')!=link_found): 
                if(anchor_link.startswith("/")): #Rebuilding the URL
                    baseURL=URL[:25] #We need to remove the "/news-analysis/" at the end of the base URL
                    anchor_link=baseURL+anchor_link #And then join it with the href
                if (company in a.get('href')) or (company in a.text) or (company.lower() in a.get('href')) or (company.lower() in a.text) \
                or (company.capitalize() in a.get('href')) or (company.capitalize() in a.text):
                    link_found=a.get('href')
                    newpage=requests.get(anchor_link)
                    newsoup=BeautifulSoup(newpage.text, "lxml")
                    article_date=newsoup.find('span', {"class":"pub-date"})['content'] #Here we extract the date on the article page
                    article_date=dateparser.parse(article_date).date()
                    article=""
                    for paragraph in newsoup.find_all('p'):
                        article+="\n"+paragraph.text
                    ta=TextAnalyzer(company, article, link_found, article_date) 
                    ta.RunAnalysis() 
                    found=True
                    print("Information found on "+anchor_link+"   "+ta.result)
                    ta.Save()
        while(article_counter<article_limit): 
            article_counter=article_counter+20
            nextpageURL=URL+"?start="+str(article_counter)
            nextpage=requests.get(nextpageURL)
            if nextpage.ok:
                soup=BeautifulSoup(nextpage.text, "lxml")
                anchors=soup.find_all('a')
                for a in anchors:
                    anchor_link=a.get('href')
                    if(anchor_link != None and a.get('href')!=link_found):
                        if(anchor_link.startswith("/")):
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
                            print("Information found on "+anchor_link+"   "+ta.result)
                            ta.Save()
            else: 
                print("Request Failure: "+nextpageURL+" returned: "+str(nextpage))
                break
        if(found==False):
            print("Could not scrape any information about "+ company+" on "+URL)
    else: 
        print("Request Failure: "+URL+" returned: "+str(mainpage))

def ScrapeCSO2(company, date):
    """
    Searches through the website "csoonline.com/news-analysis" to return a list of TextAnalyzer objects after running the analysis for each of them as well as printing the analysis result.
    If no information could be found, the function will not return anything.

    Parameters:
    -------------
    company: str
        The company name we are trying to scrape information about.

    date: date
        The date until which we scrape information. We do not search any information that is anterior to it.
    """
    string.capwords(company)
    URL="https://www.csoonline.com/news-analysis/"
    found=False
    article_counter=0

    mainpage=requests.get(URL)
    if(mainpage.ok): 
        soup=BeautifulSoup(mainpage.text, "lxml") 
        main_div=soup.find('div', {"class":"main-col"})
        anchors=main_div.find_all('a')
        link_found=""
        last_article_date=""
        for a in anchors:
            anchor_link=a.get('href')
            if(a.get('href') != None and a.get('href')!=link_found): 
                if(anchor_link.startswith("/")): 
                    baseURL=URL[:25] 
                    anchor_link=baseURL+anchor_link 
                    newpage=requests.get(anchor_link)
                    newsoup=BeautifulSoup(newpage.text, "lxml")
                    article_date=newsoup.find('span', {"class":"pub-date"})['content'] 
                    article_date=dateparser.parse(article_date).date()
                    last_article_date=article_date
                    if(article_date < date): 
                        if(found==False):
                            print("Could not find any information about "+company+" on "+URL)
                            return
                        else:
                            return
                if (company in a.get('href')) or (company in a.text) or (company.lower() in a.get('href')) or (company.lower() in a.text) \
                or (company.capitalize() in a.get('href')) or (company.capitalize() in a.text):
                    link_found=a.get('href')  
                    article=""
                    for paragraph in newsoup.find_all('p'):
                        article+="\n"+paragraph.text
                    ta=TextAnalyzer(company, article, link_found, article_date)
                    ta.RunAnalysis() 
                    found=True
                    print("Information found on "+anchor_link+"   "+ta.result)
                    ta.Save()
        while(last_article_date > date): 
            article_counter=article_counter+20
            nextpageURL=URL+"?start="+str(article_counter)
            nextpage=requests.get(nextpageURL)
            if nextpage.ok:
                soup=BeautifulSoup(nextpage.text, "lxml")
                main_div=soup.find('div', {"class":"main-col"})
                anchors=main_div.find_all('a')
                for a in anchors:
                    anchor_link=a.get('href')
                    if(anchor_link != None and a.get('href')!=link_found):
                        if(anchor_link.startswith("/")): 
                            baseURL=URL[:25]
                            anchor_link=baseURL+anchor_link
                            newpage=requests.get(anchor_link)
                            newsoup=BeautifulSoup(newpage.text, "lxml")
                            article_date=newsoup.find('span', {"class":"pub-date"})['content'] 
                            article_date=dateparser.parse(article_date).date()
                            last_article_date=article_date
                            if(article_date < date): 
                                if(found==False):
                                    print("Could not find any information about "+company+" on "+URL)
                                    return
                                else:
                                    return
                        if (company in a.get('href')) or (company in a.text) or (company.lower() in a.get('href')) or (company.lower() in a.text) \
                        or (company.capitalize() in a.get('href')) or (company.capitalize() in a.text):
                            link_found=a.get('href')
                            article=""
                            for paragraph in newsoup.find_all('p'):
                                article+="\n"+paragraph.text
                            ta=TextAnalyzer(company, article, link_found, article_date) 
                            ta.RunAnalysis()
                            found=True
                            print("Information found on "+anchor_link+"   "+ta.result)
                            ta.Save()
            else: 
                print("Request Failure: "+nextpageURL+" returned: "+str(nextpage))
                break
        if(found==False):
            print("Could not scrape any information about "+ company+" on "+URL)
    else: 
        print("Request Failure: "+URL+" returned: "+str(mainpage))

def ScrapeInfosecmag(company, page_limit=2):
    """
    Searches through the website "infosecurity-magazine.com/news" to return a list of TextAnalyzer objects after running the analysis for each of them as well as printing the analysis result.
    If no information could be found, the function will not return anything.

    Parameters:
    -------------
    company: str
        The company name we are trying to scrape information about.

    page_limit (optional): int
        The maximum number of pages the program will browse, the default value is 2.
    """
    string.capwords(company)
    URL="https://www.infosecurity-magazine.com/news/"
    found=False
    page_counter=1
    page_limit=int(page_limit)

    mainpage=requests.get(URL)
    if(mainpage.ok): 
        soup=BeautifulSoup(mainpage.text, "lxml") 
        main_div=soup.find('div' , {"id":"webpages-list"})
        anchors=main_div.find_all('a')
        link_found=""
        for a in anchors:
            if(a.get('href') != None and a.get('href')!=link_found): 
                if (company in a.get('href')) or (company in a.text) or (company.lower() in a.get('href')) or (company.lower() in a.text) \
                or (company.capitalize() in a.get('href')) or (company.capitalize() in a.text):
                    link_found=a.get('href')
                    newpage=requests.get(a.get('href'))
                    newsoup=BeautifulSoup(newpage.text, "lxml")
                    article_date=a.find('time').text 
                    article_date=dateparser.parse(article_date).date()
                    article=""
                    for paragraph in newsoup.find_all('p'):
                        article+="\n"+paragraph.text
                    ta=TextAnalyzer(company, article, link_found, article_date) 
                    ta.RunAnalysis() 
                    found=True
                    print("Information found on "+a.get('href')+"   "+ta.result)
                    ta.Save()
        while(page_counter<page_limit): 
            nextpageURL=""
            for a in soup.find_all('a'): 
                anchor=str(a)
                if("rel=\"next\"" in anchor):
                    if(a['href'].startswith("https://")):
                        nextpageURL=a['href']
            if(nextpageURL!=""):
                page_counter=page_counter+1
                nextpage=requests.get(nextpageURL)
                if nextpage.ok:
                    soup=BeautifulSoup(nextpage.text, "lxml")
                    main_div=soup.find('div' , {"id":"webpages-list"})
                    anchors=main_div.find_all('a')
                    for a in anchors:
                        if(a.get('href') != None and a.get('href')!=link_found):
                            if (company in a.get('href')) or (company in a.text) or (company.lower() in a.get('href')) or (company.lower() in a.text) \
                            or (company.capitalize() in a.get('href')) or (company.capitalize() in a.text):
                                link_found=a.get('href')
                                newpage=requests.get(a.get('href'))
                                newsoup=BeautifulSoup(newpage.text, "lxml")
                                article_date=a.find('time').text
                                article_date=dateparser.parse(article_date).date()
                                article=""
                                for paragraph in newsoup.find_all('p'):
                                    article+="\n"+paragraph.text
                                found=True
                                ta=TextAnalyzer(company, article, link_found, article_date) 
                                ta.RunAnalysis() 
                                print("Information found on "+a.get('href')+"   "+ta.result)
                                ta.Save()
                else: 
                    print("Request Failure: "+nextpageURL+" returned: "+str(nextpage))
                    break
            else: 
                break
        if(found==False):
            print("Could not find any information about "+ company+" on "+URL)
    else: 
        print("Request Failure: "+URL+" returned: "+str(mainpage))

def ScrapeInfosecmag2(company, date):
    """
    Searches through the website "infosecurity-magazine.com/news" to return a list of TextAnalyzer objects after running the analysis for each of them as well as printing the analysis result.
    If no information could be found, the function will not return anything.

    Parameters:
    -------------
    company: str
        The company name we are trying to scrape information about.

    date: date
        The date until which we scrape information. We do not search any information that is anterior to it.
    """
    string.capwords(company)
    URL="https://www.infosecurity-magazine.com/news/"
    found=False
    
    mainpage=requests.get(URL)
    if(mainpage.ok): 
        soup=BeautifulSoup(mainpage.text, "lxml") 
        main_div=soup.find('div' , {"id":"webpages-list"})
        anchors=main_div.find_all('a')
        link_found=""
        last_article_date=""
        for a in anchors:
            article_date=a.find('time').text 
            article_date=dateparser.parse(article_date).date()
            last_article_date=article_date
            if(article_date < date): 
                if(found==False):
                    print("Could not find any information about "+company+" on "+URL)
                    return
                else:
                    return
            if(a.get('href') != None and a.get('href')!=link_found):
                if (company in a.get('href')) or (company in a.text) or (company.lower() in a.get('href')) or (company.lower() in a.text) \
                or (company.capitalize() in a.get('href')) or (company.capitalize() in a.text):
                    link_found=a.get('href')
                    newpage=requests.get(a.get('href'))
                    newsoup=BeautifulSoup(newpage.text, "lxml")
                    article=""
                    for paragraph in newsoup.find_all('p'):
                        article+="\n"+paragraph.text
                    ta=TextAnalyzer(company, article, link_found, article_date) 
                    ta.RunAnalysis() 
                    found=True
                    print("Information found on "+a.get('href')+"   "+ta.result)
                    ta.Save()
        while(last_article_date > date): 
            nextpageURL=""
            for a in soup.find_all('a'): 
                anchor=str(a)
                if("rel=\"next\"" in anchor):
                    if(a['href'].startswith("https://")):
                        nextpageURL=a['href']
            if(nextpageURL!=""):
                nextpage=requests.get(nextpageURL)
                if nextpage.ok:
                    soup=BeautifulSoup(nextpage.text, "lxml")
                    main_div=soup.find('div' , {"id":"webpages-list"})
                    anchors=main_div.find_all('a')
                    for a in anchors:
                        article_date=a.find('time').text 
                        article_date=dateparser.parse(article_date).date()
                        last_article_date=article_date
                        if(article_date < date): 
                            if(found==False):
                                print("Could not find any information about "+company+" on "+URL)
                                return
                            else:
                                return
                        if(a.get('href') != None and a.get('href')!=link_found):
                            if (company in a.get('href')) or (company in a.text) or (company.lower() in a.get('href')) or (company.lower() in a.text) \
                            or (company.capitalize() in a.get('href')) or (company.capitalize() in a.text):
                                link_found=a.get('href')
                                newpage=requests.get(a.get('href'))
                                newsoup=BeautifulSoup(newpage.text, "lxml")
                                article=""
                                for paragraph in newsoup.find_all('p'):
                                    article+="\n"+paragraph.text
                                found=True
                                ta=TextAnalyzer(company, article, link_found, article_date) 
                                ta.RunAnalysis() 
                                print("Information found on "+a.get('href')+"   "+ta.result)
                                ta.Save()
                else: 
                    print("Request Failure: "+nextpageURL+" returned: "+str(nextpage))
                    break
            else: 
                break
        if(found==False):
            print("Could not find any information about "+ company+" on "+URL)
    else: 
        print("Request Failure: "+URL+" returned: "+str(mainpage))

def ScrapeNakedsec(company, page_limit=2):
    """
    Searches through the website "nakedsecurity.sophos.com" to return a list of TextAnalyzer objects after running the analysis for each of them as well as printing the analysis result.
    If no information could be found, the function will not return anything.

    Parameters:
    -------------
    company: str
        The company name we are trying to scrape information about.

    page_limit (optional): int
        The maximum number of pages the program will browse, the default value is 2.
    """
    string.capwords(company)
    URL="https://nakedsecurity.sophos.com/"
    found=False
    page_counter=1
    page_limit=int(page_limit)

    mainpage=requests.get(URL)
    if(mainpage.ok): 
        soup=BeautifulSoup(mainpage.text, "lxml") 
        anchors=soup.find_all('a')
        link_found=""
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
                    print("Information found on "+a.get('href')+"   "+ta.result)
                    ta.Save()
        while(page_counter<page_limit): 
            nextpageURL=""
            next_a=soup.find('section', {"class":"load-more"}).find('a', {"class":"button"})
            if(next_a!=None and next_a.get('href').startswith("https://")):
                nextpageURL=next_a['href']
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
                                print("Information found on "+a.get('href')+"   "+ta.result)
                                ta.Save()
                else: 
                    print("Request Failure: "+nextpageURL+" returned: "+str(nextpage))
                    break
            else: 
                break
        if(found==False):
            print("Could not scrape any information about "+ company+" on "+URL)
    else: 
        print("Request Failure: "+URL+" returned: "+str(mainpage))

def ScrapeNakedsec2(company, date):
    """
    Searches through the website "nakedsecurity.sophos.com" to return a list of TextAnalyzer objects after running the analysis for each of them as well as printing the analysis result.
    If no information could be found, the function will not return anything.

    Parameters:
    -------------
    company: str
        The company name we are trying to scrape information about.

    date: date
        The date until which we scrape information. We do not search any information that is anterior to it.
    """
    string.capwords(company)
    URL="https://nakedsecurity.sophos.com/"
    found=False

    mainpage=requests.get(URL)
    if(mainpage.ok): 
        soup=BeautifulSoup(mainpage.text, "lxml") 
        anchors=soup.find_all('a', {"rel":"bookmark"})
        link_found=""
        last_article_date=""
        for a in anchors:
            if(a.get('href') != None and a.get('href')!=link_found): 
                try:
                    newpage=requests.get(a.get('href'))
                    newsoup=BeautifulSoup(newpage.text, "lxml")
                    article_date=newsoup.find('time').text 
                    article_date=dateparser.parse(article_date).date()
                    last_article_date=article_date
                    if(article_date < date): 
                        if(found==False):
                            print("Could not find any information about "+company+" on "+URL)
                            return
                        else:
                            return
                    if (company in a.get('href')) or (company in a.text) or (company.lower() in a.get('href')) or (company.lower() in a.text) \
                    or (company.capitalize() in a.get('href')) or (company.capitalize() in a.text):
                        link_found=a.get('href')           
                        article=""
                        for paragraph in newsoup.find_all('p'):
                            article+="\n"+paragraph.text
                        ta=TextAnalyzer(company, article, link_found, article_date) 
                        ta.RunAnalysis() 
                        found=True
                        print("Information found on "+a.get('href')+"   "+ta.result)
                        ta.Save()
                except:
                    pass
        while(last_article_date > date): 
            nextpageURL=""
            next_a=soup.find('section', {"class":"load-more"}).find('a', {"class":"button"})
            if(next_a!=None and next_a.get('href').startswith("https://")):
                nextpageURL=next_a['href']
            if(nextpageURL!=""):
                nextpage=requests.get(nextpageURL)
                if nextpage.ok:
                    soup=BeautifulSoup(nextpage.text, "lxml")
                    anchors=soup.find_all('a', {"rel":"bookmark"})
                    for a in anchors:
                        if(a.get('href') != None and a.get('href')!=link_found):                           
                            try:
                                newpage=requests.get(a.get('href'))
                                newsoup=BeautifulSoup(newpage.text, "lxml")
                                article_date=newsoup.find('time').text 
                                article_date=dateparser.parse(article_date).date()
                                last_article_date=article_date
                                if(article_date < date): 
                                    if(found==False):
                                        print("Could not find any information about "+company+" on "+URL)
                                        return
                                    else:
                                        return
                                if (company in a.get('href')) or (company in a.text) or (company.lower() in a.get('href')) or (company.lower() in a.text) \
                                or (company.capitalize() in a.get('href')) or (company.capitalize() in a.text):
                                    link_found=a.get('href')
                                    article=""
                                    for paragraph in newsoup.find_all('p'):
                                        article+="\n"+paragraph.text
                                    ta=TextAnalyzer(company, article, link_found, article_date) 
                                    ta.RunAnalysis() 
                                    found=True
                                    print("Information found on "+a.get('href')+"   "+ta.result)
                                    ta.Save()
                            except:
                                pass
                else: 
                    print("Request Failure: "+nextpageURL+" returned: "+str(nextpage))
                    break
            else:
                break
        if(found==False):
            print("Could not scrape any information about "+ company+" on "+URL)
    else: 
        print("Request Failure: "+URL+" returned: "+str(mainpage))

def ScrapeKebronsec(company, page_limit=2):
    """
    Searches through the website "krebsonsecurity.com" to return a list of TextAnalyzer objects after running the analysis for each of them as well as printing the analysis result.
    If no information could be found, the function will not return anything.

    Parameters:
    -------------
    company: str
        The company name we are trying to scrape information about.

    page_limit (optional): int
        The maximum number of pages the program will browse, the default value is 2.
    """
    string.capwords(company)
    URL="https://krebsonsecurity.com/"
    found=False
    page_counter=1
    page_limit=int(page_limit)

    mainpage=requests.get(URL)
    if(mainpage.ok): 
        soup=BeautifulSoup(mainpage.text, "lxml") 
        titles=soup.find_all('h2', {"class":"entry-title"})
        link_found=""
        for title in titles:
            a=title.find('a')
            if(a.get('href') != None and a.get('href')!=link_found): 
                if (company in a.get('href')) or (company in a.text) or (company.lower() in a.get('href')) or (company.lower() in a.text) \
                or (company.capitalize() in a.get('href')) or (company.capitalize() in a.text):
                    link_found=a.get('href')
                    newpage=requests.get(a.get('href'))
                    newsoup=BeautifulSoup(newpage.text, "lxml")
                    wrapper=a.find_parent('header',{"class":"entry-header"})
                    article_date=wrapper.find('span',{"class":"date updated"}).text 
                    article_date=dateparser.parse(article_date).date()
                    article=""
                    for paragraph in newsoup.find_all('p'):
                        article+="\n"+paragraph.text
                    ta=TextAnalyzer(company, article, link_found, article_date) 
                    ta.RunAnalysis()
                    found=True
                    print("Information found on "+a.get('href')+"   "+ta.result)
                    ta.Save()
        while(page_counter<page_limit): 
            page_counter=page_counter+1
            nextpageURL="https://krebsonsecurity.com/page/{}/".format(page_counter)
            if(nextpageURL!=""):
                nextpage=requests.get(nextpageURL)
                if nextpage.ok:
                    soup=BeautifulSoup(nextpage.text, "lxml")
                    titles=soup.find_all('h2', {"class":"entry-title"})
                    for title in titles:
                        a=title.find('a')
                        if(a.get('href') != None and a.get('href')!=link_found):
                            if (company in a.get('href')) or (company in a.text) or (company.lower() in a.get('href')) or (company.lower() in a.text) \
                            or (company.capitalize() in a.get('href')) or (company.capitalize() in a.text):
                                link_found=a.get('href')
                                newpage=requests.get(a.get('href'))
                                newsoup=BeautifulSoup(newpage.text, "lxml")
                                wrapper=a.find_parent('header',{"class":"entry-header"})
                                article_date=wrapper.find('span',{"class":"date updated"}).text
                                article_date=dateparser.parse(article_date).date()
                                article=""
                                for paragraph in newsoup.find_all('p'):
                                    article+="\n"+paragraph.text
                                ta=TextAnalyzer(company, article, link_found, article_date) 
                                ta.RunAnalysis() 
                                found=True
                                print("Information found on "+a.get('href')+"   "+ta.result)
                                ta.Save()
                else: 
                    print("Request Failure: "+nextpageURL+" returned: "+str(nextpage))
                    break
            else: 
                break
        if(found==False):
            print("Could not scrape any information about "+ company+" on "+URL)
    else: 
        print("Request Failure: "+URL+" returned: "+str(mainpage))

def ScrapeKebronsec2(company, date):
    """
    Searches through the website "krebsonsecurity.com" to return a list of TextAnalyzer objects after running the analysis for each of them as well as printing the analysis result.
    If no information could be found, the function will not return anything.

    Parameters:
    -------------
    company: str
        The company name we are trying to scrape information about.

    date: date
        The date until which we scrape information. We do not search any information that is anterior to it.
    """
    string.capwords(company)
    URL="https://krebsonsecurity.com/"
    found=False
    page_counter=1

    mainpage=requests.get(URL)
    if(mainpage.ok): 
        soup=BeautifulSoup(mainpage.text, "lxml") 
        titles=soup.find_all('h2', {"class":"entry-title"})
        link_found=""
        last_article_date=""
        for title in titles:
            a=title.find('a')
            if(a.get('href') != None and a.get('href')!=link_found): 
                wrapper=a.parent.parent
                article_date=wrapper.find('span',{"class":"date updated"}).text 
                article_date=dateparser.parse(article_date).date()
                last_article_date=article_date
                if(article_date < date): 
                    if(found==False):
                        print("Could not find any information about "+company+" on "+URL)
                        return
                    else:
                        return
                if (company in a.get('href')) or (company in a.text) or (company.lower() in a.get('href')) or (company.lower() in a.text) \
                or (company.capitalize() in a.get('href')) or (company.capitalize() in a.text):
                    link_found=a.get('href')
                    newpage=requests.get(a.get('href'))
                    newsoup=BeautifulSoup(newpage.text, "lxml")                   
                    article=""
                    for paragraph in newsoup.find_all('p'):
                        article+="\n"+paragraph.text
                    ta=TextAnalyzer(company, article, link_found, article_date) 
                    ta.RunAnalysis() 
                    found=True
                    print("Information found on "+a.get('href')+"   "+ta.result)
                    #yield ta
        while(last_article_date > date): 
            page_counter=page_counter+1
            nextpageURL="https://krebsonsecurity.com/page/{}/".format(page_counter)
            if(nextpageURL!=""):
                page_counter=page_counter+1
                nextpage=requests.get(nextpageURL)
                if nextpage.ok:
                    soup=BeautifulSoup(nextpage.text, "lxml")
                    titles=soup.find_all('h2', {"class":"entry-title"})
                    for title in titles:
                        a=title.find('a')
                        if(a.get('href') != None and a.get('href')!=link_found):
                            wrapper=a.parent.parent
                            article_date=wrapper.find('span',{"class":"date updated"}).text 
                            article_date=dateparser.parse(article_date).date()
                            last_article_date=article_date
                            if(article_date < date): 
                                if(found==False):
                                    print("Could not find any information about "+company+" on "+URL)
                                    return
                                else:
                                    return
                            if (company in a.get('href')) or (company in a.text) or (company.lower() in a.get('href')) or (company.lower() in a.text) \
                            or (company.capitalize() in a.get('href')) or (company.capitalize() in a.text):
                                link_found=a.get('href')
                                newpage=requests.get(a.get('href'))
                                newsoup=BeautifulSoup(newpage.text, "lxml")                               
                                article=""
                                for paragraph in newsoup.find_all('p'):
                                    article+="\n"+paragraph.text
                                ta=TextAnalyzer(company, article, link_found, article_date) 
                                ta.RunAnalysis() 
                                found=True
                                print("Information found on "+a.get('href')+"   "+ta.result)
                                #yield ta
                else: 
                    print("Request Failure: "+nextpageURL+" returned: "+str(nextpage))
                    break
            else: 
                break
        if(found==False):
            print("Could not scrape any information about "+ company+" on "+URL)
    else:
        print("Request Failure: "+URL+" returned: "+str(mainpage))

#-----------------------------------------------------------------------------Twitter-------------------------------------------------------------------------------------------
#We are using the twitter API to scrape tweets https://developer.twitter.com/en/docs/twitter-api/getting-started/about-twitter-api || https://developer.twitter.com/en/portal/dashboard
#documentation->https://docs.tweepy.org/en/stable/client.html  /!\ 500k tweet limit per month
#To be able to run this code we highly recommend that you obtain your own API keys and copy paste them in a "keys.txt" file located in the same folder as this .py file.
# /!\ This code was designed for the free twitter API version only /!\

 
#Here we create an API client by extracting the keys from the "keys.txt" file.
def getClient():
    """
    Returns a tweepy.Client object after reading and parsing the API keys from the "keys.txt" file.

    /!\ For this function to run properly, make sure you place the keys as following (one line -> one key):
    bearer token
    consumer key
    consumer secret
    access token
    access token secret
    """
    with open("keys.txt", "r") as secretfile:
        bearer_token=secretfile.readline().rstrip()
        consumer_key=secretfile.readline().rstrip()
        consumer_secret=secretfile.readline().rstrip()
        access_token=secretfile.readline().rstrip()
        access_token_secret=secretfile.readline().rstrip()
        client=tweepy.Client(bearer_token,consumer_key,consumer_secret,access_token,access_token_secret)
    secretfile.close()
    return client

#To search tweets from a specific user, we need to get their user id first.
def getUserId(username):
    """
    Returns the id associated with the username entered as parameter.

    Parameter
    -------------
    username: str
        username of the twitter account we want to scrape tweets from.
    """
    url = 'https://api.twitter.com/2/users/by/username/{}'.format(username)

    with open("keys.txt", "r") as secretfile:
        bearer_token=secretfile.readline().rstrip()
    secretfile.close()
    headers = {'Authorization': 'Bearer {}'.format(bearer_token)}

    #We extract the user profile.
    response = requests.request('GET', url, headers = headers)
    response = response.json()
    #response = {'data': {'id': '22790881', 'name': 'briankrebs', 'username': 'briankrebs'}}
    id = response['data']['id'] #We get the id from the response dictionnary
    
    return id

#test getUserId
#username = 'briankrebs'
#print(getUserId(username)) ->22790881

# A tweet link looks like: https://twitter.com/<username>/status/<tweet_id>
def SearchTweetsUser(username, company, max_tweets):
    """
    Searches for information regarding the company we want to scrape information about through a specific user's tweets.
    Returns a list of TextAnalyzer objects after running the analysis for each of them.
    If no information could be found, the function will not return anything.

    Parameters:
    -------------
    username: str
        username of the twitter account we want to scrape tweets from.

    company: str
        the company name we are trying to scrape information about.
    
    max_tweets: int
        the amount of latest tweets we will browse from the user.
    """
    Client=getClient()
    user_id = getUserId(username)

    result=Client.get_users_tweets(user_id, exclude=['replies'],max_results=max_tweets, tweet_fields=['created_at','id','text'])
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
            
def SearchTweetsUser2(username, company, date):
    """
    Searches for information about the company we want to scrape information about through a specific user's tweets.
    Returns a list of TextAnalyzer objects after running the analysis for each of them.
    If no information could be found, the function will not return anything.

    Parameters:
    -------------
    username: str
        username of the twitter account we want to scrape tweets from.

    company: str
        the company name we are trying to scrape information about.
    
    date: date
        the date until which we will scrape tweets from the user.
    """
    string.capwords(company)
    Client=getClient()
    user_id = getUserId(username)
    date=datetime.datetime.combine(date, datetime.datetime.min.time())
    date=date.isoformat()+"Z"

    result=Client.get_users_tweets(user_id, exclude=['replies'],max_results=5, tweet_fields=['created_at','id','text'], start_time=date)
    tweets=result.data
    for tweet in tweets:
        if((company in tweet.text) or (company.lower() in tweet.text) or (company.capitalize() in tweet.text)) or(company.upper() in tweet.text):
            tweet_date=(tweet.created_at).date()
            tweet_link='https://twitter.com/{}/status/{}'.format(username, tweet.id)
            ta=TextAnalyzer(company, tweet.text, tweet_link, tweet_date)
            ta.RunAnalysis()
            yield ta

def ScrapeTwitter(company, max_tweets=10):
    """
    Searches for information through a predetermined list of twitter accounts.
    Returns a list of TextAnalyzer objects after printing the analysis result for each one of them.
    For each user, the function will browse a certain number of tweets (max_tweets parameter).

    Parameter
    -------------
    company: str
        The company name we are trying to scrape information about.

    max_tweets (optional): int
        the amount of latest tweets we will browse from each user, 10 by default.
    """
    usernames=["briankrebs", "threatpost", "peterkruse"] #This is the username list we will browse.
    Tweetlist=[]

    for user in usernames:
        for ta in SearchTweetsUser(user, company, max_tweets=max_tweets):
            Tweetlist.append(ta)

    if not Tweetlist:
        print("Could not find any information about "+company+" on Twitter.")
    else:
        for ta in Tweetlist:
            print("information found on "+ta.link+"   "+ta.result)
            ta.Save()
    #return Tweetlist

    #{'briankrebs': [<Tweet id=1481030224750026764 text=It's Patch Tuesday, Windows users! Today's batch includes fixes for something like 120 vulnerabilities, including a critical, "wormable" flaw in Windows 10/11 and later Server versions, and 3 Exchange bugs, 1 of which was reported to Microsoft by the NSA. https://t.co/zh1UdM3qZq>], 
    #'threatpost': [<Tweet id=1471484422469955585 text=@Prevailion’s PACT discovered a novel RAT, #DarkWatchman, w/ new #fileless malware techniques, sent in a Russian-language spear-phishing campaign, uniquely manipulating Windows Registry to evade most security detections. #cybersecurity https://t.co/I3HhSiNmSI>], 
    #'peterkruse': []}

def ScrapeTwitter2(company, date):
    """
    Searches for information through a predetermined list of twitter accounts.
    Returns a list of TextAnalyzer objects after printing the analysis result for each one of them.
    For each user, the function will browse the maximum amount of tweets it can before reaching the specified date entered in parameter.

    Parameter
    -------------
    company: str
        The company name we are trying to scrape information about.

    date: date
        the date until which we will scrape tweets from each user.
    """
    usernames=["briankrebs", "threatpost", "peterkruse"]
    Tweetlist=[]

    for user in usernames:
        for ta in SearchTweetsUser2(user, company, date):
            Tweetlist.append(ta)

    if not Tweetlist:
        print("Could not find any information about "+company+" on Twitter.")
    else:
        for ta in Tweetlist:
            print("information found on "+ta.link+"   "+ta.result)
            ta.Save()
    #return Tweetlist

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def textAnalyzerTest():
    text=TextAnalysis.LoadExampleText(10)
    dicMots=["cyber-attack","ransomware","attack","threatened"]
    dicPhrases=["An unsecured server has exposed sensitive data belonging to KP Snacks employees.","Cyber-criminals have attacked KP Snacks with ransomware.", 
                "KP Snacks is dealing with disruptions from a network security incident resulting from a ransomware attack.","KP Snacks was Hit by a cyberattack.", 
                "A cyberattack has struck company KP Snacks, compromising the emails of its employees.",
                "After gaining access to the company's network, hackers deployed ransomware and took the snack maker's data hostage.","KP Snacks is safe and not under attack."] #These 2 sentences are tricky on purpose
    link="https://www.infosecurity-magazine.com/news/kp-snacks-under-cyberattack/"
    article_date=dateparser.parse("3 Feb 2022").date()
    test=TextAnalyzer("SolarWinds", text, link, article_date)
    test.RunAnalysis()
    test.Save()

def WebScraping(company, page_limit=2):
    """
    Runs a global scraping over a few websites to find information about a given company and determine whether an alert should be raised or not.

    Parameters
    -------------
    company: str
        The company name we are trying to scrape information about.

    page_limit (optional): int
        The maximum number of pages the program will browse, the default value is 2.
    """
    ScrapeHackerNews(company, page_limit)
    ScrapeDarkReading(company, page_limit)
    ScrapeZDnet(company, page_limit)
    ScrapeTechRP(company, page_limit)
    ScrapeMcAfee(company, page_limit)
    ScrapeGraham(company, page_limit)
    ScrapeCSO(company, page_limit)
    ScrapeInfosecmag(company, page_limit)
    ScrapeNakedsec(company, page_limit)
    ScrapeKebronsec(company, page_limit)
    try:
        ScrapeTwitter(company)
    except:
        print("It looks like you do not have twitter API keys, have reached your tweet limit or do not have valid API keys. \
        \nAborted scraping twitter.")

def WebScraping2(company, date):
    """
    Runs a global scraping over a few websites to find information about a given company and determine whether an alert should be raised or not.

    Parameters:
    -------------
    company: str
        The company name we are trying to scrape information about.

    date: date
        The date until which we scrape information. We do not search any information that is anterior to it.
    """
    #ScrapeHackerNews2(company, date)
    #ScrapeDarkReading2(company, date)
    ScrapeZDnet2(company, date)
    #ScrapeTechRP2(company, date)
    #ScrapeMcAfee2(company, date)
    #ScrapeGraham2(company, date)
    #ScrapeCSO2(company, date)
    #ScrapeInfosecmag2(company, date)
    #ScrapeNakedsec2(company, date)
    #ScrapeKebronsec2(company, date)
    try:
        ScrapeTwitter2(company, date)
    except:
        print("It looks like you do not have twitter API keys, have reached your tweet limit or do not have valid API keys. \
        \nAborted scraping twitter.")
    
def RunProgram(companies, page_limit=2):
    """
    Searches information over a few certified sources on the internet to raise an alert whenever a company is in a state of danger or attack.

    Parameters
    -------------
    companies: list[str]
        The company names we are trying to scrape information about.

    page_limit (optional): int
        The maximum number of pages the program will browse, the default value is 2.
    """
    for company in companies:
        WebScraping(company, page_limit)

def RunProgram2(companies, date):
    """
    Searches information over a few certified sources on the internet to raise an alert whenever a company is in a state of danger or attack.

    Parameters
    -------------
    companies: list[str]
        The company names we are trying to scrape information about.

    date: date
        The date until which we scrape information. We do not search any information that is anterior to it.
    """
    try:
        date=dateparser.parse(date).date()
        limit_date=datetime.datetime(2020, 1, 1).date()
        if(date<limit_date): # past < present < future
            print("The input date is too old, by default the program will search information until "+str(limit_date))
            date=limit_date
        elif(date>datetime.datetime.today().date()):
            print("We cannot search information in the future, by default the program will search information that is up to 1 week old.")
            date=(datetime.datetime.now()-datetime.timedelta(days=7)).date()
    except:
        print("The date input is not valid, by default the program will search information that is up to 1 week old.")
        date=(datetime.datetime.now()-datetime.timedelta(days=7)).date()
    for company in companies:
        WebScraping2(company, date)

def main():
    #RunProgram2(["solarwinds"], "10 Dec 2020")
    textAnalyzerTest()

main()

