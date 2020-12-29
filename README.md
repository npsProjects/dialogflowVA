dialogflowVA

An implementation of a flask application on Dialogflow for the accounts receivable team.

Requires: 	python 3.6.8 to 3.8.3
		Pip  >20.3.3

Install macos:
1.	Navigate to project folder
2.	Run Source env\activate\bin
3.  pip install -r requirements.txt    
4.  pip install python-dotenv
5.  pip install —upgrade Dialogflow
6.	Flask run
7.	Downdload ngrok (https://ngrok.com/download)
8.	New terminal: navigate to folder of ngrok download folder
9.	Run ./ngrok http 5000
10.	Add the https link to fulfilment tab on Dialogflow (end link with /webhook)
11. To login go to the link +/login

Install Windows:
1.	Run pip install  
2.	Navigate to project folder
3.	Run virtualenv env
4.  pip install -r requirements.txt
5.	Run \env\Scripts\activate.bat
6.  pip install python-dotenv
7.  pip install —upgrade Dialogflow
8.	Downdload ngrok (https://ngrok.com/download)
9.	New terminal: navigate to folder of ngrok download folder
10.	Run ngrok http 5000
11.	Add the https link to fulfilment tab on Dialogflow (end link with /webhook)
12. To login go to the link +/login
