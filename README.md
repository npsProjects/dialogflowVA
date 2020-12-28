dialogflowVA

An implementation of a flask application on Dialogflow for the accounts receivable team.

Requires: 	python 3.6.8 to 3.8.3
		Pip  >20.3.3

Install macos:
1.	Navigate to project folder
2.	Run Source env\activate\bin
3.  pip install python-dotenv
4.  pip install —upgrade Dialogflow
5.	Flask run
6.	Downdload ngrok (https://ngrok.com/download)
7.	New terminal: navigate to folder of ngrok download folder
8.	Run ./ngrok http 5000
9.	Add the https link to fulfilment tab on Dialogflow (end link with /webhook)
10. To login go to the link +/login

Install Windows:
1.	Run pip install  
2.	Navigate to project folder
3.	Run virtualenv env
4.	Run \env\Scripts\activate.bat
5.  pip install python-dotenv
6.  pip install —upgrade Dialogflow
7.	Downdload ngrok (https://ngrok.com/download)
8.	New terminal: navigate to folder of ngrok download folder
9.	Run ngrok http 5000
9.	Add the https link to fulfilment tab on Dialogflow (end link with /webhook)
10. To login go to the link +/login
