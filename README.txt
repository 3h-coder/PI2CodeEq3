Contributors:
Hervé-Henri HOUZARD
Remy MARCHESI
Léopold DUMENIL
Lorélia KHAU AU CHEAK

--------------------------------------||About the project||--------------------------------------
Status: In development
Language: Python 3.9
Recommendations: We highly recommend that you use a 3.9+ python version as older versions may not be
compatible with the project. We also recommend that you use your own twitter API keys, however note that this
project only supports the free twitter API. Please make sure you install all the dependencies from the
"requirements.txt" file in your environment before trying to run the program.

SHORT DESCRIPTION:
The goal of this project is to develop an alert tool that searches information online about given companies, 
raises alerts after text analysis and saves them whenever one of these companies has gone through a cyberattack
or is at state of high risk (mostly due to a vulnerability).

LONG DESCRIPTION:
The idea is for the program to run permanently in the background of its user's machine. The user specifies a list
of companies to watch over, while the program continuously searches information about each company in the list.
In order to do that, the program loops through 11 different websites (more might be added as development progresses) 
considered to be secured sources. For instance, https://thehackernews.com/ is one them. Once a targeted company is
mentionned in an article (or tweet), the program then performs analysis to determine whether or not the article/tweet
content is worth raising an alert, and saves all analysis data into a specific object called TextAnalyzer.
Currently, there are 3 levels of alert. Level 1 being a possibility of attack/breachwhereas level 3 suggests that an 
attack or vulnerability event is certain. Finally, in between, level 2 suggests a high probability of a critical event.
The reason why we return several alert levels is because false positives may occur, and thus when checking each raised 
alert the user can prioritize high level alerts over low level ones. After analysis, the TextAnalyzer object is saved
into a .txt file (the saving medium might be changed later on) located in the analysis_results folder.
Before running the analysis, the user may specify a date until which the program will search information, by default
it will not be able to search any information that is anterior to January 1st 2020.
It is important to note that the program only searches for English information.

Development details:
-The analysis function is currently flawed as it returns too many false positives, fixing this issue is our main priority.
-Currently the project is meant to be used by people with a minimum of knowledge around python development, we are 
considering making it open to a wider variety of users and thus increasing it's accessibility through a UI or GUI application.
