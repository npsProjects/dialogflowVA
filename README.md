dialogflowVA

An implementation of a flask application on Dialogflow for the accounts receivable team.

Requires: 	python 3.6.8 to 3.8.3
		Pip  >20.3.3

Install macos:
1.	Navigate to project folder
2.	Run Source env\activate\bin
3.	Flask run
4.	Downdload ngrok (https://ngrok.com/download)
5.	New terminal: navigate to folder of ngrok download folder
6.	Run ./ngrok http 5000
7.	Add link to fulfilment tab on Dialogflow

Install Windows:
1.	Run pip install  
2.	Navigate to project folder
3.	Run virtualenv env
4.	Run \env\Scripts\activate.bat
5.	Downdload ngrok (https://ngrok.com/download)
6.	New terminal: navigate to folder of ngrok download folder
7.	Run ngrok http 5000
8.	Add link + \webhook to fulfilment tab on Dialogflow
