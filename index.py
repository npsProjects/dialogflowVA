# /index.py
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import sqlite3
from sqlite3 import Error
import os
import dialogflow_v2beta1 as dialogflow
import requests
import json
from datetime import date

app = Flask(__name__)

app.secret_key = "any random string"

user = "CanforUser1"
client_id = 'Canfor'
@app.route('/chatbot/<username>')
def index(username):
    # session['my_var'] = username
    global user
    global client_id
    user = username
    print("USER IS:" + str(user))
    client_id = str(query("SELECT client_id  FROM user where user_id = \"" + str(user)+"\"")[0])
    client_id = client_id[2:]
    client_id=client_id[:(len(client_id)-3)]
    print(client_id + " Is the custom er-------------------------------")

    # my_var = session.get('my_var', None)
    # print("TEST___________________"+str(query("SELECT client_id  FROM client_user_table where user_id = \"" + my_var+"\"")))
    # session['client_id'] = str(query("SELECT client_id  FROM client_user_table where user_id = \"" + my_var+"\"")[0])
    #
    # customer_id = session['client_id']
    #
    # print(customer_id + " Is the custom er")


    name = str(query("SELECT name  FROM user where user_id = \"" + str(user)+"\"")[0])
    name = name[2:]
    name = name[:(len(name)-3)]
    return render_template('index.html', name = name,  client_id = client_id )

# Route for handling the login page logic
@app.route('/login', methods=['GET', 'POST'])
def login():
    print("USER IS:" + str(user))
    error = None
    if request.method == 'POST':
        return redirect(url_for('index', username=request.form['username']))
    else:
        return render_template('login.html', error=error)

@app.route('/webhook', methods=['POST'])
def webhook():
    # Print the request if we want to see it
    if request.method == 'POST':
        print(request.json)
    req = request.get_json(silent=True, force=True)
    query_result = req.get('queryResult')
    # What we are going to return at the end.
    result = []
    queryGoal = ''


    print("Customer is:" + str(user))
    if(query_result.get('intent').get('displayName')=='credit_intent'):

        # Define different variables for table values
        # resultAmountAvailable = []
        # resultAmountUsed = []
        # resultCreditRating = []
        # maxLen = 0
        payer = 0
        # Get the payer name
        payer_id = ''

        if(len(query_result.get('parameters').get('payer_id'))>0):
            payer_id = query_result.get('parameters').get('payer_id')[0]
            print(type(payer_id))

        if (len(payer_id)>0):
            payer = 1

        if (payer == 1 ):
            queryGoal = str("SELECT payer_id,amount_available,amount_used,amount_remaining,credit_rating  FROM credit_history where payer_id = \"" + payer_id+"\"" + " and client_id = \"" + client_id + "\"")
        else:
            queryGoal = str("SELECT payer_id,amount_available,amount_used,amount_remaining,credit_rating  FROM credit_history where client_id = \"" + client_id + "\"")

        queryGraph = str("SELECT DISTINCT payer_id FROM credit_history where client_id = \"" + client_id + "\"")
        graphInformation = query(queryGraph)
        graphMessage = []
        for g in graphInformation:
            # print("--------------------------" + str(g)[2: len(g)-4])
            graphMessage.append(str(g)[2: len(g)-4])
            graphMessage.append(query(str("SELECT Count(*)  FROM invoices where invoice_paid = \"no\" and payer_id = \"" + str(g)[2: len(g)-4]) +"\"" + " and client_id = \"" + client_id + "\""))

        # print("--------------------------" + str(graphMessage))
        resultModification= query(queryGoal)
        if ( len(resultModification) == 0):
            return jsonify(fulfillmentText=str("You do not have access to this information. Please choose a different payer credit information."),
                       displayText='25',
                       id="webhookdata")

        result.append("Type3")
        result.append("|")
        # result.append("Credit history ID")
        # result.append("Client ID")
        result.append("Payer ID")
        result.append("Credit available")
        result.append("Credit used")
        result.append("Credit remaining")
        result.append("Credit rating")

        # p = 0;
        for row in resultModification:
            result.append(row)
            # result.append("<br>")

        result.append("|")
        if user == "CanforUser2":
            result.append("De informatie wordt weergegeven in de tabellen aan de linkerkant.")
        else:
            result.append("The information is displayed in the tables on the left.")
        result.append("|")
        result.append(graphMessage)
        result.append("|")
        result.append("Credit information")
        return jsonify(fulfillmentText=str(result),
                   displayText='25',
                   id="webhookdata")

        #Below is division by columns on the answers (Currently not required)
        # if(len(query_result.get('parameters').get('amountavailable'))!=0):
        #     resultAmountAvailable = query("SELECT amount_available  FROM credit_history_table where payer_id = \"" + payer_id+"\"" + " AND customer_id = \"" + customer_id + "\"")
        #     print("The result is:" + str(len(resultAmountAvailable)))
        #     maxLen = len(resultAmountAvailable)
        #
        # if(query_result.get('parameters').get('amountused')!=''):
        #     resultAmountUsed = query("SELECT amount_used  FROM credit_history_table where payer_id = \"" + payer_id+"\"" + " AND customer_id = \"" + customer_id + "\"")
        #     print("The result is:" + str(resultAmountUsed))
        #     maxLen = len(resultAmountUsed)
        #
        # if(query_result.get('parameters').get('creditrating')!=''):
        #     resultCreditRating = query("SELECT credit_rating  FROM credit_history_table where payer_id = \"" + payer_id +"\"" + " AND customer_id = \"" + customer_id + "\"")
        #     print("The result is:" + str(resultCreditRating))
        #     maxLen = len(resultCreditRating)
        #
        # for i in range(0, maxLen):
        #     print(i)
        #     result.append(i)
        #     if (len(resultAmountAvailable)!= 0):
        #         print("Amount available: " + str(resultAmountAvailable[i]))
        #         result.append("Amount available: " + str(resultAmountAvailable[i]))
        #     if (len(resultAmountUsed)!= 0):
        #         print("Amount used: " + str(resultAmountUsed[i]))
        #         result.append("Amount used: " + str(resultAmountUsed[i]))
        #     if (len(resultCreditRating)!= 0):
        #         print("Creadit rating: " + str(resultCreditRating[i]))
        #         result.append("Credit rating: " + str(resultCreditRating[i]))

    if(query_result.get('intent').get('displayName')=='payerIntent'):

        resultAdress = []
        resultIBAN1 = []
        resultIBAN2 = []
        maxLen = 0

        payer = 0
        # Get the payer name
        payer_id = ''

        if(len(query_result.get('parameters').get('payer_id'))>0):
            payer_id = query_result.get('parameters').get('payer_id')[0]
            print(type(payer_id))

        if (len(payer_id)>0):
            payer = 1

        if (payer == 1 ):
            queryGoal = str("SELECT payer_name,payer_address,payer_IBAN  FROM payer where payer_id = \"" + payer_id+"\"" + " and client_id = \"" + client_id + "\"")
        else:
            queryGoal = str("SELECT payer_name,payer_address,payer_IBAN  FROM payer where client_id = \"" + client_id + "\"")

        resultModification= query(queryGoal)
        # print(type(resultModification))

        resultModification= query(queryGoal)
        if ( len(resultModification) == 0):
            return jsonify(fulfillmentText=str("You do not have access to this information. Please choose a different payer credit information."),
                       displayText='25',
                       id="webhookdata")

        result.append("Type1")
        result.append("|")
        # result.append("Payer ID")
        result.append("Payer Name")
        result.append("Payer Address")
        result.append("Payer IBAN")
        # result.append("Client ID")
        # result.append("<br>")

        for row in resultModification:
            result.append(row)
            # result.append("<br>")

        result.append("|")

        if user == "CanforUser2":
            result.append("De informatie wordt weergegeven in de tabellen aan de linkerkant.")
        else:
            result.append("The information is displayed in the tables on the left.")

        result.append("|")
        result.append("Payer information")
        return jsonify(fulfillmentText=str(result),
                   displayText='25',
                   id="webhookdata")

        #Below is division by columns on the answers (Currently not required)
        # if(len(query_result.get('parameters').get('payer_id'))>1):
        #     payer_id = query_result.get('parameters').get('payer_id')
        # elif(len(query_result.get('parameters').get('payer_id'))>0):
        #     payer_id = query_result.get('parameters').get('payer_id')
        #
        # if(query_result.get('parameters').get('address')!=''):
        #     resultAdress = query("SELECT payer_address  FROM payer_table where payer_id = \"" + payer_id+"\"")
        #     print("The result is:" + str(len(resultAdress)))
        #     maxLen = len(resultAdress)
        #
        # if(query_result.get('parameters').get('primaryiban')!=''):
        #     resultIBAN1 = query("SELECT payer_IBAN1  FROM payer_table where payer_id = \"" + payer_id+"\"")
        #     print("The result is:" + str(resultIBAN1))
        #     maxLen = len(resultIBAN1)
        #
        # if(query_result.get('parameters').get('secondaryiban')!=''):
        #     resultIBAN2 = query("SELECT payer_IBAN2  FROM payer_table where payer_id = \"" + payer_id +"\"")
        #     print("The result is:" + str(resultIBAN2))
        #     maxLen = len(resultIBAN2)
        #
        # for i in range(0, maxLen):
        #     print(i)
        #     result.append(i)
        #     if (len(resultAdress)!= 0):
        #         print("Payer Adress: " + str(resultAdress[i]))
        #         result.append("Payer Adress: " + str(resultAdress[i]))
        #     if (len(resultIBAN1)!= 0):
        #         print("IBAN1: " + str(resultIBAN1[i]))
        #         result.append("IBAN1: " + str(resultIBAN1[i]))
        #     if (len(resultIBAN2)!= 0):
        #         print("IBAN2: " + str(resultIBAN2[i]))
        #         result.append("IBAN2: " + str(resultIBAN2[i]))
        #
        # return {
        #     "fulfillmentText": str(result),#query_result.get('fulfillmentText'),
        #     "displayText": '25',
        #     "source": "webhookdata"
        # }

    if(query_result.get('intent').get('displayName')=='InvoiceIntent'):
        print(query_result.get('intent').get('displayName'))

        print("Determine whether Select or Count: \n")

        if(len(query_result.get('parameters').get('count'))>0):
            print(str(query_result.get('parameters').get('count')))
            count = True
            queryGoal = str("SELECT count(*)  FROM invoices where client_id = \"" + client_id + "\"")

        if(len(query_result.get('parameters').get('selectSQL'))>0):
            print(str(query_result.get('parameters').get('selectSQL')))
            select = True
            count = False
            queryGoal = str("SELECT *  FROM invoices where client_id = \"" + client_id + "\"")

        print("Query for now is: \n" + str(queryGoal))

        payer_id = ''
        if(len(query_result.get('parameters').get('payer_id'))>0):
            payer_id = query_result.get('parameters').get('payer_id')[0]

        payer = 0
        if (len(payer_id)>0):
            payer = 1

        if (payer == 1 ):
            queryGoal = queryGoal + str(" and payer_id = \"" + payer_id+"\"")
        else:
            queryGoal = queryGoal

        print("Query for now is: \n" + str(queryGoal))

        percentage=100
        amountbol = 0
        if(len(query_result.get('parameters').get('more')) > 0 and len(query_result.get('parameters').get('number-integer')) > 0):
            print(str(query_result.get('parameters').get('more')))
            amountbol = 1
            amount = query_result.get('parameters').get('number-integer')[0]
            queryGoal= queryGoal + (" AND amount_remaining >= " + str(int(amount)))

        elif(len(query_result.get('parameters').get('less')) > 0 and len(query_result.get('parameters').get('number-integer')) > 0):
            print(str(query_result.get('parameters').get('less')))
            amountbol = -1
            amount = query_result.get('parameters').get('number-integer')[0]
            queryGoal= queryGoal + (" AND amount_remaining <= " + str(int(amount)))

        elif(len(query_result.get('parameters').get('number-integer')) > 0):
            amount = query_result.get('parameters').get('number-integer')[0]
            queryGoal= queryGoal + (" AND invoice_amount == " + str(int(amount)))

        elif(len(query_result.get('parameters').get('top')) > 0 and len(query_result.get('parameters').get('percentage')) > 0 ):
            amountbol=2
            percentage = int(query_result.get('parameters').get('percentage')[0][:2])

        elif(len(query_result.get('parameters').get('lowest')) > 0)and len(query_result.get('parameters').get('percentage')) > 0 :
            amountbol=-2
            percentage = int(query_result.get('parameters').get('percentage')[0][:2])

        elif(len(query_result.get('parameters').get('top')) > 0 ):
            amountbol=2
            percentage = 1

        elif(len(query_result.get('parameters').get('lowest')) > 0):
            amountbol=-2
            percentage = 1


        print(amountbol)
        print("Query for now is: \n" + str(queryGoal))

        paid = -1
        paidw = 'no'

        if(len(query_result.get('parameters').get('paid')) > 0):
            print(str(query_result.get('parameters').get('paid')))
            paid = 1
            paidw = 'yes'

        if(len(query_result.get('parameters').get('notPaid')) > 0):
            print(str(query_result.get('parameters').get('notPaid')))
            paid = -1
            paidw = 'no'


        dateDialogflow = ''

        if(len(query_result.get('parameters').get('overdue'))>0 and len(query_result.get('parameters').get('date-time'))>0):

            paid = -1
            paidw = 'no'
            from datetime import date
            today = date.today()
            d1 = today.strftime("%d/%m/%Y")

            days = str(query_result.get('parameters').get('date-time')[0])
            firstMonth = int(days[24:26])
            firstDay = int(days[27:29])
            secondMonth = int(days[68:70])
            secondDay = int(days[71:73])

            if( secondMonth > firstMonth):
                secondDay = secondDay + (30*(secondMonth-firstMonth))

            period = secondDay - firstDay
            print(period)

            months = int(str(d1[3:5]))
            days = int(str(d1[:2]))

            print(days)
            if(days > period):
                days = days - period
            elif(period > days):
                m = (period)/30
                m = int(m + 1)
                days = (m * 30) + days - period
                months = months - m

            print(days)
            print(months)
            if(days < 10):
                days = str("0" + str(days))
            else:
                days = str(days)

            if(months < 10):
                months = str("0" + str(months))
            else:
                months = str(months)

            dateDialogflow = (str(d1[6:10])+ ':' + months + ':' + days)
            queryGoal = queryGoal + str(" and invoice_due_date <= \"" + dateDialogflow + "\"")


        elif(len(query_result.get('parameters').get('overdue'))>0):
            paid = -1
            paidw = 'no'
            from datetime import date
            today = date.today()
            # dd/mm/YY
            d1 = today.strftime("%d/%m/%Y")
            print("d1 =", d1)
            dateDialogflow = (str(d1[6:10])+ ':' + str(d1[3:5]) + ':' + str(d1[:2]))
            queryGoal = queryGoal + str(" and invoice_due_date <= \"" + dateDialogflow + "\"")

        elif(len(query_result.get('parameters').get('date-time'))>0 and len(query_result.get('parameters').get('before'))>0):
            dateDialogflow = str(query_result.get('parameters').get('date-time')[0])
            dateDialogflow = (dateDialogflow[0:4] + ':' + dateDialogflow[5:7] + ':' + dateDialogflow[8:10])
            queryGoal = queryGoal + str(" and invoice_due_date <= \"" + dateDialogflow + "\"")

        elif(len(query_result.get('parameters').get('date-time'))>0 and len(query_result.get('parameters').get('after'))>0):
            dateDialogflow = str(query_result.get('parameters').get('date-time')[0])
            dateDialogflow = (dateDialogflow[0:4] + ':' + dateDialogflow[5:7] + ':' + dateDialogflow[8:10])
            queryGoal = queryGoal + str(" and invoice_due_date >= \"" + dateDialogflow + "\"")

        elif(len(query_result.get('parameters').get('date-time'))>0):

            days = str(query_result.get('parameters').get('date-time')[0])
            if (len(days)>70):
                # firstMonth = int(days[24:26])
                # firstDay = int(days[27:29])
                # secondMonth = int(days[68:70])
                # secondDay = int(days[71:73])

                dateDialogflow = (str(days[15:19])+ ':' + str(days[20:22]) + ':' + str(days[23:25]))
                dateDialogflow2 = (str(days[55:59])+ ':' + str(days[60:62]) + ':' + str(days[63:65]))
                queryGoal = queryGoal + str(" and invoice_due_date >= \"" + dateDialogflow + "\"")
                queryGoal = queryGoal + str(" and invoice_due_date <= \"" + dateDialogflow2 + "\"")

                # if( secondMonth > firstMonth):
                #     secondDay = secondDay + (30*(secondMonth-firstMonth))
                #
                # period = secondDay - firstDay
                # print(period)
                #
                # months = int(str(d1[3:5]))
                # days = int(str(d1[:2]))
                #
                # print(days)
                # if(days > period):
                #     days = days - period
                # elif(period > days):
                #     m = (period)/30
                #     m = int(m + 1)
                #     days = (m * 30) + days - period
                #     months = months - m
                #
                # print(days)
                # print(months)
                # if(days < 10):
                #     days = str("0" + str(days))
                # else:
                #     days = str(days)
                #
                # if(months < 10):
                #     months = str("0" + str(months))
                # else:
                #     months = str(months)
                #
                # dateDialogflow = (str(d1[6:10])+ ':' + months + ':' + days)
                # queryGoal = queryGoal + str(" and invoice_due_date <= \"" + dateDialogflow + "\"")

            else:
                dateDialogflow = str(query_result.get('parameters').get('date-time')[0])
                dateDialogflow = (dateDialogflow[0:4] + ':' + dateDialogflow[5:7] + ':' + dateDialogflow[8:10])
                queryGoal = queryGoal + str(" and invoice_due_date <= \"" + dateDialogflow + "\"")

        print("Query for now is: \n" + str(queryGoal))


        if(paid!=0):
            queryGoal = queryGoal + str(" and invoice_paid =  \"" + paidw + "\"")

        queryGoal = queryGoal + str(" order by amount_remaining DESC")
        print("Query for now is: \n" + str(queryGoal))


        resultModification= query(queryGoal)
        # print(type(resultModification))


        if (count==True):
            return jsonify(fulfillmentText=str(resultModification),
                       displayText='25',
                       id="webhookdata")


        print(percentage)
        percentage = 100/percentage
        print(percentage)
        length = int(len(resultModification)/percentage)
        if (length == 0):
            length = 1
        print(int(length))
        result.append("Type1")
        result.append("|")
        result.append("Invoice ID")
        result.append("Invoice issued by")
        result.append("Payer ID")
        result.append("Invoice amount")
        result.append("Amount paid")
        result.append("Amount remaining")
        result.append("Invoice date")
        result.append("Invoice due date")
        result.append("Invoice paid")
        # result.append("<br>")



        if(amountbol==2):
            resultModification = (resultModification[:length])
        elif(amountbol==-2):
            resultModification = (resultModification[(int(len(resultModification)))-length:(int(len(resultModification)))])

        for row in resultModification:
            result.append(row)
            # result.append("<br>")
        result.append("|")
        if user == "CanforUser2":
            result.append("De informatie wordt weergegeven in de tabellen aan de linkerkant.")
        else:
            result.append("The information is displayed in the tables on the left.")
        result.append("|")
        result.append("Invoices")
        return jsonify(fulfillmentText=str(result),
                   displayText='25',
                   id="webhookdata")


    # DIALOGBUILDINGPART

    if(query_result.get('intent').get('displayName')=='seeInvoicesIntentYes'):
        print(query_result.get('intent').get('displayName'))

        queryGoal = str("SELECT *  FROM invoices where client_id = \"" + client_id + "\"" + "and invoice_paid = \"no\"")
        dateDialogflow = ("2020:12:09")
        queryGoal = queryGoal + str(" and invoice_due_date <= \"" + dateDialogflow + "\"" + " order by amount_remaining DESC")


        resultModification= query(queryGoal)

        # length = int(len(resultModification)/20)
        #
        # if (length == 0):
        #     length = 1
        # resultModification = (resultModification[:length])

        result.append("Type1")
        result.append("|")
        result.append("Invoice ID")
        result.append("Invoice issued by")
        result.append("Payer ID")
        result.append("Invoice amount")
        result.append("Amount paid")
        result.append("Amount remaining")
        result.append("Invoice date")
        result.append("Invoice due date")
        result.append("Invoice paid")


        for row in resultModification:
            result.append(row)

        result.append("|")


        queryGoal = str("SELECT payer_id  FROM invoices where client_id = \"" + client_id + "\"" + "and invoice_paid = \"no\"")
        dateDialogflow = ("2020:12:09")
        queryGoal = queryGoal + str(" and invoice_due_date <= \"" + dateDialogflow + "\"" + " order by amount_remaining DESC" )

        resultTarget = query(queryGoal)
        length = int(len(resultTarget))
        namePayer = str(resultTarget[0])
        length = int(len(namePayer))
        namePayer = namePayer[2:length-3]

        result.append(str("You can see the information on the tables on the left. The invoice with the highest amount is from " + namePayer + ". Would you like to see more information about them?"))
        result.append("|")
        result.append("Invoices")


        return jsonify(fulfillmentText=str(result),
                   displayText='25',
                   id="webhookdata")

    if(query_result.get('intent').get('displayName')=='seeInvoicesIntentYesYes'):
        print(query_result.get('intent').get('displayName'))

        queryGoal = str("SELECT payer_id  FROM invoices where client_id = \"" + client_id + "\"" + "and invoice_paid = \"no\"")
        dateDialogflow = ("2020:12:09")
        queryGoal = queryGoal + str(" and invoice_due_date <= \"" + dateDialogflow + "\"" + " order by amount_remaining DESC" )

        resultTarget = query(queryGoal)
        length = int(len(resultTarget))
        namePayer = str(resultTarget[0])
        length = int(len(namePayer))
        namePayer = namePayer[2:length-3]



        queryGoal = str("SELECT *  FROM invoices where client_id = \"" + client_id + "\"" + "and payer_id = \"" + namePayer + "\"" + "and invoice_paid = \"no\"")

        resultModification= query(queryGoal)
        result.append("Type2")
        result.append("|")
        result.append("Invoice ID")
        result.append("Invoice issued by")
        result.append("Payer ID")
        result.append("Invoice amount")
        result.append("Amount paid")
        result.append("Amount remaining")
        result.append("Invoice date")
        result.append("Invoice due date")
        result.append("Invoice paid")


        for row in resultModification:
            result.append(row)
        #
        #     # -----------------------------------
        # queryGoalAV = str("SELECT amount_available  FROM credit_history_table where payer_id = \"" + payer_id+"\"" + " AND customer_id = \"" + customer_id + "\"")
        # queryGoalAR = str("SELECT amount_remaining  FROM credit_history_table where payer_id = \"" + payer_id+"\"" + " AND customer_id = \"" + customer_id + "\"")
        #
        # AV = query(queryGoalAV)
        # AR = query(queryGoalAR)




            # ----------------------------------

        queryGoal = str("SELECT payer.payer_name,payer.payer_address,payer.payer_IBAN,credit_history.amount_available,credit_history.amount_used,credit_history.amount_remaining,credit_history.credit_rating  FROM payer, credit_history where credit_history.payer_id = \"" + namePayer+"\" and credit_history.payer_id = \"" + namePayer+"\"" + "and payer.payer_id = \"" + namePayer+"\"" + " AND credit_history.client_id = \"" + client_id + "\"" + "and payer.client_id = \"" + client_id + "\"")

        resultModification= query(queryGoal)
        print(type(resultModification))
        # payer_name,payer_address,payer_IBAN        payer_id,amount_available,amount_used,amount_remaining,credit_rating
        result.append("|")
        # result.append("Payer ID")
        result.append("Payer Name")
        result.append("Payer Address")
        result.append("Payer IBAN")
        # result.append("Credit history ID")
        # result.append("Customer ID")
        # result.append("Client ID")
        # result.append("Payer ID")
        result.append("Credit available")
        result.append("Credit used")
        result.append("Credit remaining")
        result.append("Credit rating")


        for row in resultModification:
            result.append(row)


        result.append("|")
        result.append(str("You can see the information about " + namePayer + " on the tables on the left. Would you like to contact them."))

        result.append("|")
        result.append(str("Invoices for "+namePayer))
        result.append("|")
        result.append(str(namePayer + " information"))

        return jsonify(fulfillmentText=str(result),
                   displayText='25',
                   id="webhookdata")

    if(query_result.get('intent').get('displayName')=='seeInvoicesIntentYesYesYes'):
        print(query_result.get('intent').get('displayName'))

        queryGoal = str("SELECT payer_id  FROM invoices where client_id = \"" + client_id + "\"" + "and invoice_paid = \"no\"")
        dateDialogflow = ("2020:12:09")
        queryGoal = queryGoal + str(" and invoice_due_date <= \"" + dateDialogflow + "\"" + " order by amount_remaining DESC" )

        resultTarget = query(queryGoal)
        length = int(len(resultTarget))
        namePayer = str(resultTarget[0])
        length = int(len(namePayer))
        namePayer = namePayer[2:length-3]

        result.append("Type4")
        result.append("|")
        result.append(namePayer)
        result.append("|")

        queryGoal = str("SELECT payer_address  FROM payer where client_id = \"" + client_id + "\"" + " and payer_id = \""+ namePayer + "\"")
        resultTarget = query(queryGoal)
        length = int(len(resultTarget))
        address = str(resultTarget[0])
        length = int(len(address))
        address = address[2:length-3]
        result.append(address)
        result.append("|")


        queryGoal = str("SELECT invoice_id  FROM invoices where client_id = \"" + client_id + "\"" + "and invoice_paid = \"no\"")
        dateDialogflow = ("2020:12:09")
        queryGoal = queryGoal + str(" and invoice_due_date <= \"" + dateDialogflow + "\"" + " order by amount_remaining DESC" )

        resultTarget = query(queryGoal)
        length = int(len(resultTarget))
        invoiceid = str(resultTarget[0])
        length = int(len(invoiceid))
        invoiceid = invoiceid[2:length-3]

        result.append(invoiceid)
        result.append("|")

        queryGoal = str("SELECT invoice_due_date  FROM invoices where client_id = \"" + client_id + "\"" + "and invoice_paid = \"no\"")
        dateDialogflow = ("2020:12:09")
        queryGoal = queryGoal + str(" and invoice_due_date <= \"" + dateDialogflow + "\"" + " order by amount_remaining DESC" )

        resultTarget = query(queryGoal)
        length = int(len(resultTarget))
        date = str(resultTarget[0])
        length = int(len(date))
        date = date[2:length-3]

        result.append(date)
        result.append("|")

        queryGoal = str("SELECT invoice_amount  FROM invoices where client_id = \"" + client_id + "\"" + "and invoice_paid = \"no\"")
        dateDialogflow = ("2020:12:09")
        queryGoal = queryGoal + str(" and invoice_due_date <= \"" + dateDialogflow + "\"" + " order by amount_remaining DESC" )
        resultTarget = query(queryGoal)

        resultTarget = query(queryGoal)
        length = int(len(resultTarget))
        invoice_amount = str(resultTarget[0])
        length = int(len(invoice_amount))
        invoice_amount = invoice_amount[1:length-2]

        result.append(invoice_amount)
        result.append("|")

        name = str(query("SELECT name  FROM user where user_id = \"" + str(user)+"\"")[0])
        name = name[2:]
        name = name[:(len(name)-3)]

        result.append(name)
        result.append("|")

        result.append(client_id)
        # result.append("|")

        # result.append(resultTarget[0])

        return jsonify(fulfillmentText=str(result),
                   displayText='25',
                   id="webhookdata")


    # results.append(response.query_result.fulfillment_text)
    result.append("Sorry, this is a virtual assistant for the accounts receivable team and the virtual cash management domain. Perhaps a different  assistant can answer your question.")
    return jsonify(fulfillmentText=str(result),
               displayText='25',
               id="webhookdata")

def detect_intent_texts(project_id, session_id, text, language_code):
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)
    print('Session path: '+ str(session))

    if text:
        text_input = dialogflow.types.TextInput(
            text=text, language_code=language_code)
        print("Text input is" + str(text_input))
        query_input = dialogflow.types.QueryInput(text=text_input)
        print("query input is" + str(query_input))

        knowledge_base_id="MzIwODA5MTI1NTg1MDQwMTc5Mg"
        knowledge_base_path = dialogflow.knowledge_bases_client \
            .KnowledgeBasesClient \
            .knowledge_base_path(project_id, knowledge_base_id)

        query_params = dialogflow.types.QueryParameters(
            knowledge_base_names=[knowledge_base_path])
        print('=' * 20)
        print(query_params)
        response = session_client.detect_intent(
            session=session, query_input=query_input,
            query_params=query_params)


        # response = session_client.detect_intent(
        #     session=session, query_input=query_input)
        print('=' * 20)
        print('Query text: {}'.format(response.query_result.query_text))
        print('Detected intent: {} (confidence: {})\n'.format(
            response.query_result.intent.display_name,
            response.query_result.intent_detection_confidence))
        print('Fulfillment text: {}\n'.format(
            response.query_result.fulfillment_text))
        return response.query_result.fulfillment_text

@app.route('/send_message', methods=['POST'])
def send_message():
    message = request.form['message']
    project_id = os.getenv('DIALOGFLOW_PROJECT_ID')
    if user == "CanforUser2":
        fulfillment_text = detect_intent_texts(project_id, "unique", message, 'nl')
    else:
        fulfillment_text = detect_intent_texts(project_id, "unique", message, 'en')
    response_text = { "message":  fulfillment_text }
    print(response_text)
    return jsonify(response_text)

@app.route('/send_message2', methods=['POST'])
def send_message2():
    if user == "CanforUser2":
        return "Hallo, ik ben uw virtuele cashmanagement-assistent. Hoe kan ik je vandaag helpen?"
    else:
        return "Hello, I am your virtual cash management assistant. How can I help you today?"


def query(query):
    print(" I am querying:  " + query)
    database = (r"tt.db")
    conn = None
    try:
        conn = sqlite3.connect(database)
    except Error as e:
        print(e)
    with conn:
        print("Query is")
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    for row in rows:
        print(row)

    return rows

# run Flask app
if __name__ == "__main__":
    app.run()
