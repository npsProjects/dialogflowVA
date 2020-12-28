# /index.py
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import sqlite3
from sqlite3 import Error
import os
import dialogflow_v2beta1 as dialogflow
import requests
import json
from datetime import date

# Required for connecting to dialogflow, app name
app = Flask(__name__)
app.secret_key = "any random string"

# We specify a default user to make sure we can use it without logging in (just in case)
user = "CanforUser1"
client_id = 'Canfor'

# Route for handling the login page logic
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        return redirect(url_for('index', username=request.form['username']))
    else:
        return render_template('login.html', error=error)


# Main page
# Render and specify user
@app.route('/chatbot/<username>')
def index(username):
    global user
    global client_id
    print("----------------------------------------------------------------------------------------")

    user = username
    print("* User is:" + str(user))

    client_id = str(query("SELECT client_id  FROM user where user_id = \"" + str(user)+"\"")[0])
    client_id=client_id[2:(len(client_id)-3)]

    print("* Customer is:" + str(client_id))
    print("----------------------------------------------------------------------------------------")

    name = str(query("SELECT name  FROM user where user_id = \"" + str(user)+"\"")[0])
    name = name[2:]
    name = name[:(len(name)-3)]
    return render_template('index.html', name = name,  client_id = client_id )


# The webhook. The intents specified with fullfillment in the dialogflow will be redirected here.
@app.route('/webhook', methods=['POST'])
def webhook():
    print("-----------------------WEBHOOK--------------------")

    # Print the request
    if request.method == 'POST':
        print(request.json)
    req = request.get_json(silent=True, force=True)
    query_result = req.get('queryResult')

    # we define the result and the query we are going to perform.
    result = []
    queryGoal = ''

    # Deal with the credit intent here
    if(query_result.get('intent').get('displayName')=='credit_intent'):
        print("-----------------------Credit intent--------------------")
        # Specify the payer and payer Flag (if there is a payer)
        # Then query based on the result from dialogflow.
        payer = 0
        payer_id = ''

        if(len(query_result.get('parameters').get('payer_id'))>0):
            payer_id = query_result.get('parameters').get('payer_id')[0]

        if (len(payer_id)>0):
            payer = 1

        if (payer == 1 ):
            queryGoal = str("SELECT payer_id,amount_available,amount_used,amount_remaining,credit_rating  FROM credit_history where payer_id = \"" + payer_id+"\"" + " and client_id = \"" + client_id + "\"")
        else:
            queryGoal = str("SELECT payer_id,amount_available,amount_used,amount_remaining,credit_rating  FROM credit_history where client_id = \"" + client_id + "\"")

        # FIll information about the graph.
        queryGraph = str("SELECT DISTINCT payer_id FROM credit_history where client_id = \"" + client_id + "\"")
        graphInformation = query(queryGraph)
        graphMessage = []
        for g in graphInformation:
            graphMessage.append(str(g)[2: len(g)-4])
            graphMessage.append(query(str("SELECT Count(*)  FROM invoices where invoice_paid = \"no\" and payer_id = \"" + str(g)[2: len(g)-4]) +"\"" + " and client_id = \"" + client_id + "\""))

        # Create the result table info, but keep it separate for modification
        resultModification= query(queryGoal)

        # IF our result is empty we probably asked for info we dont have /dont have access to.
        if ( len(resultModification) == 0):
            return jsonify(fulfillmentText=str("You do not have access to this information. Please choose a different payer credit information."),
                       displayText='25',
                       id="webhookdata")

        # Append the head of the table.
        # Type 3 means graph + table

        result.append("Type3")
        result.append("|")
        # result.append("Credit history ID")
        # result.append("Client ID")
        result.append("Payer ID")
        result.append("Credit available")
        result.append("Credit used")
        result.append("Credit remaining")
        result.append("Credit rating")

        # Append table info
        for row in resultModification:
            result.append(row)

        # Append message based on Language of User
        result.append("|")
        if user == "CanforUser2":
            result.append("De informatie wordt weergegeven in de tabellen aan de linkerkant.")
        else:
            result.append("The information is displayed in the tables on the left.")

        # Append graph data and name of table.
        result.append("|")
        result.append(graphMessage)
        result.append("|")
        result.append("Credit information")
        return jsonify(fulfillmentText=str(result),
                   displayText='25',
                   id="webhookdata")

    # Deal with the payer intent here
    if(query_result.get('intent').get('displayName')=='payerIntent'):

        print("-----------------------Payer Intent--------------------")

        # Specify the payer and payer Flag (if there is a payer)
        # Then query based on the result from dialogflow.
        payer = 0
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

        # Create the result table info, but keep it separate for modification
        resultModification= query(queryGoal)
        # IF we have no result here probably we asked info we dont ave acces to
        if ( len(resultModification) == 0):
            return jsonify(fulfillmentText=str("You do not have access to this information. Please choose a different payer credit information."),
                       displayText='25',
                       id="webhookdata")

        # Type 1 just one table
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

        # Append message show in chat
        result.append("|")
        if user == "CanforUser2":
            result.append("De informatie wordt weergegeven in de tabellen aan de linkerkant.")
        else:
            result.append("The information is displayed in the tables on the left.")
        # Table name
        result.append("|")
        result.append("Payer information")
        return jsonify(fulfillmentText=str(result),
                   displayText='25',
                   id="webhookdata")

    # Deal with the invoice intent here
    if(query_result.get('intent').get('displayName')=='InvoiceIntent'):
        print("-----------------------Invoice Intent--------------------")

        print(" * Determine whether Select or Count: \n")

        if(len(query_result.get('parameters').get('count'))>0):
            print(str(query_result.get('parameters').get('count')))
            count = True
            queryGoal = str("SELECT count(*)  FROM invoices where client_id = \"" + client_id + "\"")

        if(len(query_result.get('parameters').get('selectSQL'))>0):
            print(str(query_result.get('parameters').get('selectSQL')))
            select = True
            count = False
            queryGoal = str("SELECT *  FROM invoices where client_id = \"" + client_id + "\"")

        print(" * Query for now is: \n" + str(queryGoal))


        print(" * Determine whether we have a payer or we want all: \n")
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

        print(" * Query for now is: \n" + str(queryGoal))

        print(" * Determine whether we deal with amount or percentage")
        percentage=100
        amountbol = 0
        # This is if we have more than an amount
        if(len(query_result.get('parameters').get('more')) > 0 and len(query_result.get('parameters').get('number-integer')) > 0):
            print(str(query_result.get('parameters').get('more')))
            amountbol = 1
            amount = query_result.get('parameters').get('number-integer')[0]
            queryGoal= queryGoal + (" AND amount_remaining >= " + str(int(amount)))

        # Less than an amount
        elif(len(query_result.get('parameters').get('less')) > 0 and len(query_result.get('parameters').get('number-integer')) > 0):
            print(str(query_result.get('parameters').get('less')))
            amountbol = -1
            amount = query_result.get('parameters').get('number-integer')[0]
            queryGoal= queryGoal + (" AND amount_remaining <= " + str(int(amount)))
        # If it equals
        elif(len(query_result.get('parameters').get('number-integer')) > 0):
            amount = query_result.get('parameters').get('number-integer')[0]
            queryGoal= queryGoal + (" AND invoice_amount == " + str(int(amount)))
        # If top something percent
        elif(len(query_result.get('parameters').get('top')) > 0 and len(query_result.get('parameters').get('percentage')) > 0 ):
            amountbol=2
            percentage = int(query_result.get('parameters').get('percentage')[0][:2])
        # IF lowest something percent
        elif(len(query_result.get('parameters').get('lowest')) > 0)and len(query_result.get('parameters').get('percentage')) > 0 :
            amountbol=-2
            percentage = int(query_result.get('parameters').get('percentage')[0][:2])
        # The top invoice
        elif(len(query_result.get('parameters').get('top')) > 0 ):
            amountbol=2
            percentage = 1
        # The less invoice
        elif(len(query_result.get('parameters').get('lowest')) > 0):
            amountbol=-2
            percentage = 1

        print(" * Query for now is: \n" + str(queryGoal))

        print(" * Determine whether we deal with paid or unpaid invoices (Default unpaid)")
        # paid boolean and paidW is the word (yes,no)
        paid = -1
        paidw = 'no'
        if(len(query_result.get('parameters').get('paid')) > 0):
            print(str(query_result.get('parameters').get('paid')))
            paid = 1
            paidw = 'yes'
            print(" * We are dealing with paid invoices.")
        # This is used if default is all invoices
        # if(len(query_result.get('parameters').get('notPaid')) > 0):
        #     print(str(query_result.get('parameters').get('notPaid')))
        #     paid = -1


        print(" * Determine whether we deal with date")
        dateDialogflow = ''
        # If we are dealing with overdue invoices
        if(len(query_result.get('parameters').get('overdue'))>0 and len(query_result.get('parameters').get('date-time'))>0):
            # Since they are overdue they are not paid
            paid = -1
            paidw = 'no'
            # Import the today's date (import is here because it otherwise does not work)
            from datetime import date
            today = date.today()
            d1 = today.strftime("%d/%m/%Y")

            # Get the number of days (So dialogflow gives us a time period and we calculate how long it is)
            days = str(query_result.get('parameters').get('date-time')[0])
            firstMonth = int(days[24:26])
            firstDay = int(days[27:29])
            secondMonth = int(days[68:70])
            secondDay = int(days[71:73])

            if( secondMonth > firstMonth):
                secondDay = secondDay + (30*(secondMonth-firstMonth))

            period = secondDay - firstDay
            months = int(str(d1[3:5]))
            days = int(str(d1[:2]))
            # If we are dealing with period from previous month
            if(days > period):
                days = days - period
            elif(period > days):
                m = (period)/30
                m = int(m + 1)
                days = (m * 30) + days - period
                months = months - m

            if(days < 10):
                days = str("0" + str(days))
            else:
                days = str(days)

            if(months < 10):
                months = str("0" + str(months))
            else:
                months = str(months)
            # Put together the date we need to look before
            dateDialogflow = (str(d1[6:10])+ ':' + months + ':' + days)

            queryGoal = queryGoal + str(" and invoice_due_date <= \"" + dateDialogflow + "\"")


        # IF just overdue this means just invoices which are not paid AND (Different from previous one) past their due date.
        elif(len(query_result.get('parameters').get('overdue'))>0):
            paid = -1
            paidw = 'no'
            from datetime import date
            today = date.today()
            # dd/mm/YY
            d1 = today.strftime("%d/%m/%Y")
            dateDialogflow = (str(d1[6:10])+ ':' + str(d1[3:5]) + ':' + str(d1[:2]))
            queryGoal = queryGoal + str(" and invoice_due_date <= \"" + dateDialogflow + "\"")
        # If before some date (This is not used anymore) (Always before date)
        elif(len(query_result.get('parameters').get('date-time'))>0 and len(query_result.get('parameters').get('before'))>0):
            dateDialogflow = str(query_result.get('parameters').get('date-time')[0])
            dateDialogflow = (dateDialogflow[0:4] + ':' + dateDialogflow[5:7] + ':' + dateDialogflow[8:10])
            queryGoal = queryGoal + str(" and invoice_due_date <= \"" + dateDialogflow + "\"")
        # After (same as above)
        elif(len(query_result.get('parameters').get('date-time'))>0 and len(query_result.get('parameters').get('after'))>0):
            dateDialogflow = str(query_result.get('parameters').get('date-time')[0])
            dateDialogflow = (dateDialogflow[0:4] + ':' + dateDialogflow[5:7] + ':' + dateDialogflow[8:10])
            queryGoal = queryGoal + str(" and invoice_due_date >= \"" + dateDialogflow + "\"")
        # If we just say date
        elif(len(query_result.get('parameters').get('date-time'))>0):
            # First if is if we are dealing with a period. Example: Last week, Last month, November etc...
            days = str(query_result.get('parameters').get('date-time')[0])
            if (len(days)>70):
                dateDialogflow = (str(days[15:19])+ ':' + str(days[20:22]) + ':' + str(days[23:25]))
                dateDialogflow2 = (str(days[55:59])+ ':' + str(days[60:62]) + ':' + str(days[63:65]))
                queryGoal = queryGoal + str(" and invoice_due_date >= \"" + dateDialogflow + "\"")
                queryGoal = queryGoal + str(" and invoice_due_date <= \"" + dateDialogflow2 + "\"")


            else:
                dateDialogflow = str(query_result.get('parameters').get('date-time')[0])
                dateDialogflow = (dateDialogflow[0:4] + ':' + dateDialogflow[5:7] + ':' + dateDialogflow[8:10])
                queryGoal = queryGoal + str(" and invoice_due_date <= \"" + dateDialogflow + "\"")

        print("Query for now is: \n" + str(queryGoal))

        # If they are not all of them add ( it was already showed above) whether yes or no
        if(paid!=0):
            queryGoal = queryGoal + str(" and invoice_paid =  \"" + paidw + "\"")

        queryGoal = queryGoal + str(" order by amount_remaining DESC")
        print("Query for now is: \n" + str(queryGoal))


        resultModification= query(queryGoal)
        # If we are dealing with count invoices
        if (count==True):
            return jsonify(fulfillmentText=str(resultModification),
                       displayText='25',
                       id="webhookdata")

        # Type 1 is just table
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


        # If we are dealing with percentage get the percent.
        percentage = 100/percentage
        length = int(len(resultModification)/percentage)
        if (length == 0):
            length = 1

        if(amountbol==2):
            resultModification = (resultModification[:length])
        elif(amountbol==-2):
            resultModification = (resultModification[(int(len(resultModification)))-length:(int(len(resultModification)))])

        for row in resultModification:
            result.append(row)
            # result.append("<br>")
        # Response based on language
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
        print("-----------------------Invoice Dialog 1--------------------")
        #This is the same as the invoice intent, however we always take the top 10 invoices pending today
        queryGoal = str("SELECT *  FROM invoices where client_id = \"" + client_id + "\"" + "and invoice_paid = \"no\"")
        dateDialogflow = ("2020:12:09")
        queryGoal = queryGoal + str(" and invoice_due_date <= \"" + dateDialogflow + "\"" + " order by amount_remaining DESC")

        resultModification= query(queryGoal)

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

        # Find the name in the highest invoice
        queryGoal = str("SELECT payer_id  FROM invoices where client_id = \"" + client_id + "\"" + "and invoice_paid = \"no\"")
        # Current day
        from datetime import date
        today = date.today()
        # dd/mm/YY
        d1 = today.strftime("%d/%m/%Y")
        dateDialogflow = (str(d1[6:10])+ ':' + str(d1[3:5]) + ':' + str(d1[:2]))

        queryGoal = queryGoal + str(" and invoice_due_date <= \"" + dateDialogflow + "\"" + " order by amount_remaining DESC" )
        namePayer = queryParse(queryGoal)

        # Message
        result.append(str("You can see the information on the tables on the left. The invoice with the highest amount is from " + namePayer + ". Would you like to see more information about them?"))
        result.append("|")
        result.append("Invoices")


        return jsonify(fulfillmentText=str(result),
                   displayText='25',
                   id="webhookdata")

    if(query_result.get('intent').get('displayName')=='seeInvoicesIntentYesYes'):
        print("-----------------------Invoice Dialog 2--------------------")
        # First create the invoices table
        queryGoal = str("SELECT payer_id  FROM invoices where client_id = \"" + client_id + "\"" + "and invoice_paid = \"no\"")
        # Current day
        from datetime import date
        today = date.today()
        # dd/mm/YY
        d1 = today.strftime("%d/%m/%Y")
        dateDialogflow = (str(d1[6:10])+ ':' + str(d1[3:5]) + ':' + str(d1[:2]))

        queryGoal = queryGoal + str(" and invoice_due_date <= \"" + dateDialogflow + "\"" + " order by amount_remaining DESC" )

        namePayer = queryParse(queryGoal)

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

        # Get the full info from credit and payer table that we want.
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

        # MEssage
        result.append("|")
        result.append(str("You can see the information about " + namePayer + " on the tables on the left. Would you like to contact them."))

        # First table name
        result.append("|")
        result.append(str("Invoices for "+namePayer))
        # Second table name
        result.append("|")
        result.append(str(namePayer + " information"))

        return jsonify(fulfillmentText=str(result),
                   displayText='25',
                   id="webhookdata")

    if(query_result.get('intent').get('displayName')=='seeInvoicesIntentYesYesYes'):
        print("-----------------------Invoice Dialog 3--------------------")

        queryGoal = str("SELECT payer_id  FROM invoices where client_id = \"" + client_id + "\"" + "and invoice_paid = \"no\"")
        # Current day
        from datetime import date
        today = date.today()
        # dd/mm/YY
        d1 = today.strftime("%d/%m/%Y")
        dateDialogflow = (str(d1[6:10])+ ':' + str(d1[3:5]) + ':' + str(d1[:2]))

        queryGoal = queryGoal + str(" and invoice_due_date <= \"" + dateDialogflow + "\"" + " order by amount_remaining DESC" )

        namePayer = queryParse(queryGoal)
        # Type 4 is generating an email. We attach the info required for the template we currently have
        result.append("Type4")
        result.append("|")
        result.append(namePayer)
        result.append("|")

        queryGoal = str("SELECT payer_address  FROM payer where client_id = \"" + client_id + "\"" + " and payer_id = \""+ namePayer + "\"")
        address = queryParse(queryGoal)
        result.append(address)
        result.append("|")


        queryGoal = str("SELECT invoice_id  FROM invoices where client_id = \"" + client_id + "\"" + "and invoice_paid = \"no\"")
        queryGoal = queryGoal + str(" and invoice_due_date <= \"" + dateDialogflow + "\"" + " order by amount_remaining DESC" )
        invoiceid = queryParse(queryGoal)
        result.append(invoiceid)
        result.append("|")

        queryGoal = str("SELECT invoice_due_date  FROM invoices where client_id = \"" + client_id + "\"" + "and invoice_paid = \"no\"")
        queryGoal = queryGoal + str(" and invoice_due_date <= \"" + dateDialogflow + "\"" + " order by amount_remaining DESC" )
        date = queryParse(queryGoal)
        result.append(date)
        result.append("|")

        queryGoal = str("SELECT invoice_amount  FROM invoices where client_id = \"" + client_id + "\"" + "and invoice_paid = \"no\"")
        queryGoal = queryGoal + str(" and invoice_due_date <= \"" + dateDialogflow + "\"" + " order by amount_remaining DESC" )
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

        return jsonify(fulfillmentText=str(result),
                   displayText='25',
                   id="webhookdata")

    print("-----------------------WEBHOOK--------------------")
    # If we reach here we detected intent that we cant answer.
    result.append("Sorry, this is a virtual assistant for the accounts receivable team and the virtual cash management domain. Perhaps a different  assistant can answer your question.")
    return jsonify(fulfillmentText=str(result),
               displayText='25',
               id="webhookdata")

# Here we send the message to dialogflow. We need to specify the knowledge base since it is still a beta feature and requires this.
def detect_intent_texts(project_id, session_id, text, language_code):
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)
    print(' * Session path: '+ str(session))

    if text:
        text_input = dialogflow.types.TextInput(
            text=text, language_code=language_code)
        print("* Text input is: " + str(text_input))

        query_input = dialogflow.types.QueryInput(text=text_input)
        print(" * Query input is " + str(query_input))

        # We can check this by going to dialogflow and answering a question from the knowledge base. Going to details helps us with this.
        knowledge_base_id="MzIwODA5MTI1NTg1MDQwMTc5Mg"
        knowledge_base_path = dialogflow.knowledge_bases_client \
            .KnowledgeBasesClient \
            .knowledge_base_path(project_id, knowledge_base_id)


        query_params = dialogflow.types.QueryParameters(
            knowledge_base_names=[knowledge_base_path])
        print(" * Query params is: " + str(query_params))

        response = session_client.detect_intent(
            session=session, query_input=query_input,
            query_params=query_params)

        print('Query text: {}'.format(response.query_result.query_text))
        print('Detected intent: {} (confidence: {})\n'.format(
            response.query_result.intent.display_name,
            response.query_result.intent_detection_confidence))
        print('Fulfillment text: {}\n'.format(
            response.query_result.fulfillment_text))

        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        return response.query_result.fulfillment_text

# Reroute to detect intent with the required information. lso specify language here.-
@app.route('/send_message', methods=['POST'])
def send_message():
    print("----------------------------------------------------------------------------------------")
    message = request.form['message']
    project_id = os.getenv('DIALOGFLOW_PROJECT_ID')

    if user == "CanforUser2":
        fulfillment_text = detect_intent_texts(project_id, "unique", message, 'nl')
    else:
        fulfillment_text = detect_intent_texts(project_id, "unique", message, 'en')
    response_text = { "message":  fulfillment_text }
    print(" * Response from dialogflow: " + str(response_text))
    print("----------------------------------------------------------------------------------------")
    return jsonify(response_text)

# The initial message. Here we specify the different languages first response.
@app.route('/send_first_message', methods=['POST'])
def submit_first_message():
    if user == "CanforUser2":
        return "Hallo, ik ben uw virtuele cashmanagement-assistent. Hoe kan ik je vandaag helpen?"
    else:
        return "Hello, I am your virtual cash management assistant. How can I help you today?"

# Perform the query
def query(query):
    print(" ~~~~~~~~~~")
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
    # Print the results to see them
    for row in rows:
        print(" \/ ")
        print(row)
    print("~~~~~~~~~")
    return rows

# Results from query to be parsed ( remove, () etc...)
def queryParse(inputQuery):
    target = query(inputQuery)
    target = str(target[0])
    length = int(len(target))
    target = target[2:length-3]
    return target

# run Flask app
if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0')

@app.route('/')
def hello_world():
    return render_template('index.html')
