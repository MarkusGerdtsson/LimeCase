from os import stat
from flask import Flask, render_template
from datetime import datetime
from dateutil import parser
import requests
import json
# Feel free to import additional libraries if you like

app = Flask(__name__, static_url_path='/static')

# Paste the API-key you have received as the value for "x-api-key"
headers = {
        "Content-Type": "application/json",
        "Accept": "application/hal+json",
        "x-api-key": "860393E332148661C34F8579297ACB000E15F770AC4BD945D5FD745867F590061CAE9599A99075210572"
}


# Example of function for REST API call to get data from Lime
def get_api_data(headers, url):
    # First call to get first data page from the API
    response = requests.get(url=url,
                            headers=headers,
                            data=None,
                            verify=False)

    # Convert response string into json data and get embedded limeobjects
    json_data = json.loads(response.text)
    limeobjects = json_data.get("_embedded").get("limeobjects")

    # Check for more data pages and get thoose too
    nextpage = json_data.get("_links").get("next")
    while nextpage is not None:
        url = nextpage["href"]
        response = requests.get(url=url,
                                headers=headers,
                                data=None,
                                verify=False)

        json_data = json.loads(response.text)
        limeobjects += json_data.get("_embedded").get("limeobjects")
        nextpage = json_data.get("_links").get("next")

    return limeobjects


# Index page
@app.route('/')
def index():
    return render_template('home.html')


@app.route('/averagedeals')
def averagedeals():
    #Won deals last year (2021)
    base_url = "https://api-test.lime-crm.com/api-test/api/v1/limeobject/company/35362/deal/"
    params = "?dealstatus=agreement&min-closeddate=2021-01-01T00:01Z&max-closeddate=2021-12-12T23:59Z"
    url = base_url + params
    response_deals = get_api_data(headers=headers, url=url)

    companies = []
    dates = []
    value = []


    sum = 0
    avragevalue = 0
    
    for deals in response_deals:
        sum += deals['value']
        date = deals['closeddate']


        yourdate = parser.parse(date)
        newdate = datetime.strftime(yourdate, '%y/%m/%d')

        companies.append(deals['name'])
        dates.append(newdate)
        value.append(deals['value'])
            
        #Jag försökte något såhär men fick ej att fungera:
        #yourdate = parser.parse(date)
        #newdate = datetime.strftime(yourdate, '%y/%m/%d')
        #date['closeddate'] = json.loads(newdate)
        #newestdate = json.loads(newdate)
        #print(newdate)
        #date['closeddate'] = json.loads(json.dumps([newdate]))

    avragevalue = sum // (len(response_deals)+1)

    lenght = len(companies)

    return render_template('averagedeals.html', response_deals = response_deals, sum = sum, avragevalue = avragevalue, companies=companies, dates=dates, value=value, lenght=lenght)

@app.route('/dealspermonth')
def dealspermonth():
    #Number of deals per month last year (2021)
    base_url = "https://api-test.lime-crm.com/api-test/api/v1/limeobject/company/35362/deal/"
    params = "?dealstatus=agreement&min-closeddate=2021-01-01T00:01Z&max-closeddate=2021-12-12T23:59Z"
    url = base_url + params
    response_deals = get_api_data(headers=headers, url=url)

    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

    numofdeals = [0,0,0,0,0,0,0,0,0,0,0,0]
    valuelist = [0,0,0,0,0,0,0,0,0,0,0,0]
    for deals in response_deals:

        date = deals['closeddate']
        value = deals['value']
        
        yourdate = parser.parse(date)
        newdate = datetime.strftime(yourdate, '%m')

        numofdeals[int(newdate) -1] += 1
        valuelist[int(newdate)-1] += int(value)

    
    return render_template('dealspermonth.html', months= months, numofdeals = numofdeals , valuelist=valuelist)


@app.route('/dealspercustomer')
def dealspercustomer():
    #Number of deals per month last year (2021)
    base_url = "https://api-test.lime-crm.com/api-test/api/v1/limeobject/company/35362/deal/"
    params = "?dealstatus=agreement&min-closeddate=2021-01-01T00:01Z&max-closeddate=2021-12-12T23:59Z"
    url = base_url + params
    response_deals = get_api_data(headers=headers, url=url)

    customers = []
    valueofdeals = []
    numofdeals = []

    for deals in response_deals:

        customer = deals['name']
        value = deals['value']
        print(value)
        
        if customer in customers:
            valueofdeals[customers.index(customer)] += deals['value']
            numofdeals[customers.index(customer)] += 1

        else:
            customers.append(customer)
            valueofdeals.append(value)
            numofdeals.append(1)


    lenght = len(customers) 


    return render_template('dealspercustomer.html', customers=customers, valueofdeals=valueofdeals, numofdeals=numofdeals, lenght=lenght)


@app.route('/statusofcompanies')
def statusofcompanies():
    #Number of deals per month last year (2021)
    base_url = "https://api-test.lime-crm.com/api-test/api/v1/limeobject/company/35362/deal/"
    params = "?"
    url = base_url + params
    response_deals = get_api_data(headers=headers, url=url)

    companies =  []
    status = []

    date = datetime.now()
    month = "{:02d}".format(date.month)

    #Active customers
    customersparams = "?dealstatus=agreement&min-closeddate="+str((date.year-1))+"-"+str(month)+"-"+str(date.day)+"T00:01Z&max-closeddate="+str(date.year)+"-"+str(month)+"-"+str(date.day)+"T23:59Z"
    custurl = base_url + customersparams
    customers = get_api_data(headers=headers, url=custurl)

    for customer in customers:
        if customer['name'] not in companies:
            companies.append(customer['name'])
            status.append("Customer")
        
    #Inactive customers
    inactiveparams = "?dealstatus=agreement&max-closeddate="+str((date.year-1))+"-"+str(month)+"-"+str(date.day)+"T00:01Z"
    inacurl = base_url + inactiveparams
    inactivecustomers = get_api_data(headers=headers, url=inacurl)

    for inactive in inactivecustomers:
        if inactive['name'] not in companies:
            companies.append(inactive['name'])
            status.append("Inactive")

    #Prospect customers
    for allcustomer in response_deals:
        if allcustomer['name'] not in companies:
            if allcustomer['dealstatus'] == 'notinterested':
                pass
            else:
                companies.append(allcustomer['name'])
                status.append("prospect")
        
    numofcompanies = len(companies)

    return render_template('statusofcompanies.html', companies=companies, status=status, numofcompanies=numofcompanies)

# DEBUGGING
"""
If you want to debug your app, one of the ways you can do that is to use:
import pdb; pdb.set_trace()
Add that line of code anywhere, and it will act as a breakpoint and halt
your application
"""

if __name__ == '__main__':
    app.secret_key = 'somethingsecret'
    app.run(debug=True)
