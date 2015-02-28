import re
import requests, json, urllib, cookielib
import Levenshtein
import unicodedata
from bs4 import BeautifulSoup

class OurGroceries:
    url = 'https://www.ourgroceries.com'
    email = ''
    password = ''
    cookie = None
    session = False
    shoppinglists = None
    teamId = None
    LevenshteinThreshold = None
    prepositions = ['from','to']

    def __init__(self, email, password, LevenshteinThreshold=0.57):
        self.email = email
        self.password = password
        self.session = requests.Session()
        self.LevenshteinThreshold = LevenshteinThreshold
        self.login()

    def login(self):
        print "OurGroceries logging in..."

        # Get the login page and retrieve our form action.
        loginPage = self.get('/sign-in')
        loginSoup = BeautifulSoup(loginPage.text)

        form = loginSoup.find('form')
        action = self.url+form.get('action')

        # Create our parameter payload
        parameters = {}
        parameters['emailAddress'] = self.email
        parameters['password'] = self.password
        parameters['action'] = 'sign-me-in'
        parameters['staySignedIn'] = 'on'

        # Set up the headers for the request
        headers = self.getHeaders()
        headers['Referer'] = '/sign-in'

        # Now, we can create a new post request to log in
        login = self.session.post(action, data=parameters, headers=headers)

        self.cookie = self.session.cookies.get_dict()

        self.shoppinglists = self.var2dict(self.getjsvar(login.text, 'g_shoppingLists'))
        self.teamId = self.getjsvar(login.text, 'g_teamId').split('=')[1].strip().strip('\"')

    def smartinsert(self, sentence):
        # find the shopping list base on string metric distance
        words = [word.lower() for word in sentence.split(' ')]
        shoppinglist = None
        llr = 0
        llrk = None
        for w in words:
            for k in self.shoppinglists.keys():
                # find the word with the largest LR
                #lr = Levenshtein.ratio(w, k.encode('ascii','ignore'))
                lr = Levenshtein.ratio(w, k)
                if lr > llr:
                    llr = lr
                    llrk = k

        # check that the largest LR is larger than the LR threshold
        if llr > self.LevenshteinThreshold:
            shoppinglist = llrk
        else:
            shoppinglist = 'placeless'

        # everything before the preposition is consider the item of interest
        item = 'Empty'
        for p in self.prepositions:
            if p in words:
                item = ' '.join(words[:words.index(p)])
       
        print ''
        print 'sentence:', sentence
        print 'll:',llr,', llrk:', llrk
        print 'item:', item

        # now add it to the shopping list
        return self.insertitem(item, shoppinglist)
        
    def insertitem(self, item, shoppinglist):
        shoppinglist = shoppinglist.lower()
        if shoppinglist not in self.shoppinglists:
            return 'bonk'

        parameters = {}
        parameters['command'] = 'insertItem'
        parameters['listId'] = self.shoppinglists[shoppinglist]
        parameters['teamId'] = self.teamId
        parameters['value'] = item

        headers = self.getHeaders()
        headers['Referer'] = '/your-lists'
        headers['Content-Type'] = 'application/json'

        print 'adding',item,'to',shoppinglist

        resp = self.session.post(self.url+'/your-lists/', data=json.dumps(parameters), headers=headers, cookies=self.cookie)
        print 'resp:', resp.status_code

        return resp.status_code

    def get(self, url, data=False):
        headers = self.getHeaders()
        return self.session.get(self.url + url, headers=headers, params=data)

    ## Prepare common headers that we send with all requests.
    def getHeaders(self):
        headers = {}
        headers['User-Agent'] = 'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2.13) Gecko/20101206 Ubuntu/10.10 (maverick) Firefox/3.6.13'
        headers['Charset'] = 'utf-8'
        headers['Origin'] = 'https://www.ourgroceries.com'
        headers['Referer'] = 'http://www.ourgroceries.com/your-lists'
        return headers

    def getjsvar(self, text, var):
        start = text.find(var)
        length = text[start:].find(';')
        return text[start:start+length]
   
    def var2dict(self, text):
        d = {}
        varlist=re.findall("\{(.*?)\}", text)
        for var in varlist:
            kv = var.split(',')
            key = kv[1].split(':')[1].strip(' ').strip('\"').lower()
            val = kv[0].split(':')[1].strip(' ').strip('\"')
            d[key] = val
   
        return d
 
