from flask import Flask, render_template
import requests
import json
# Feel free to import additional libraries if you like

app = Flask(__name__, static_url_path='/static')

# Paste the API-key you have received as the value for "x-api-key"
headers = {
        "Content-Type": "application/json",
        "Accept": "application/hal+json",
        "x-api-key": ""
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


# Example page
@app.route('/example')
def example():

    # Example of API call to get deals
    base_url = "https://api-test.lime-crm.com/api-test/api/v1/limeobject/deal/"
    params = "?_limit=50"
    url = base_url + params
    response_deals = get_api_data(headers=headers, url=url)

    """
    [YOUR CODE HERE]
    In this exmaple, this is where you can do something with the data in
    'response_deals' before you return it below.
    """

    if len(response_deals) > 0:
        return render_template('example.html', deals=response_deals)
    else:
        msg = 'No deals found'
        return render_template('example.html', msg=msg)


# You can add more pages to your app, like this:
@app.route('/myroute')
def myroute():
    mydata = [{'name': 'apple'}, {'name': 'mango'}, {'name': 'banana'}]
    """
    For mytemplate.html to rendered you have to create the mytemplate.html
    page inside the templates-folder. And then add a link to your page in the
    _navbar.html-file, located in templates/includes/
    """
    return render_template('mytemplate.html', items=mydata)

@app.route('/testplate')
def testplate():
    
    return render_template('testplate.html')

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
