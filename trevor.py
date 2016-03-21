# Matthew Jack

import sys
import os
import json
import re
import string
import xml.etree.ElementTree as ET
from urllib.request import HTTPHandler, Request, build_opener
from flask import Flask, render_template, request
app = Flask(__name__)
# Web app stuff

@app.route('/')
def main():
    return render_template('index.html')

@app.route("/get_params", methods=['GET'])
def get_params():
    disease = request.args.get('disease', '')
    num_articles = request.args.get('num_articles', '')
    num_words = request.args.get('num_words', '')
    instance = trevor(disease, num_articles, num_words)
    return view_data()

@app.route("/view_data", methods=['GET'])
def view_data():
    return render_template('data.html')

# Python stuff

class trevor:

    def __init__(self, disease="celiac", num_articles="100", num_words="50"):
        # Start it up
        handler = docHandler(disease, num_articles)
        # Get UIDs of the documents we want
        # CHANGE
        uids = handler.get_uids()
        # Format the data to be traversed
        abstracts = handler.get_abstracts(uids)
        # Calculate word frequencies
        indexer = traverseText(abstracts)
        index = indexer.freqList
        # Create data visualization
        viz = dataViz(index, num_words)
        viz.populateJSON()
        # Done!

class dataViz:

    def __init__(self, index, num_words="50"):
        self.index = index
        self.sizeFactor = 825
        self.num_words = num_words

    def populateJSON(self):
        print(" [+] Generating visualization...")
        # Create JSON skeleton
        skeleton = self.index[:int(self.num_words)]
        # Get rid of pesky empty lists
        skeleton = [x for x in skeleton if x]
        master = {}
        jsonString = "{ \"name\": \"Visual Medicine\",\"children\": [ "
        # Generate the JSON visualization data
        i = 0
        for parent in skeleton:
            temp = list()
            temp.append(dict(name=parent[0], size=int(parent[1])*self.sizeFactor))
            master.update(name=parent[0], children=temp)
            i += 1
            jsonString = jsonString + json.dumps(master, indent=3) + ","

        jsonString = jsonString[:-1] + " ] }"
        # Write to file
        f = open('static/data.json', 'w')
        f.write(jsonString)
        f.close()
        return

class traverseText:
    # Algorithm:
    # - Create a dictionary of unspecified size
    # - Increment dict[word] by 1 each time word is encountered
    # --- if dict[word] does not exist, create it and set it to 1
    # - Sort, print.

    def __init__(self, text):
        # Using a dict initiatlly because
        # it's easy to stick a value in a key
        # Set up vars
        self.text = text
        self.freqDict = dict()
        self.freqList = []
        self.omit = self.loadOmitWords("static/omit_words")
        # Run methods
        self.buildWordIndex()
        self.sortWordIndex()

    def loadOmitWords(self, filename):
        omit = []
        f = open(filename, 'r')
        words = f.read()
        for word in words.split():
            omit.append(word)
        return omit

    def buildWordIndex(self):
        print(" [+] Building index...")
        regex = re.compile('[%s]' % re.escape(string.punctuation))
        for paper in self.text:
            # Now we're in a list that holds one abstract
            for word in paper:
                # Now it's a string
                for word in word.split():
                    # Down to words
                    if self.evaluateWord(word):
                        if word not in self.freqDict:
                            self.freqDict[regex.sub('', word.lower())] = 1
                        else:
                            self.freqDict[regex.sub('', word.lower())] += 1
        return

    def sortWordIndex(self):
        for key in self.freqDict:
            self.freqList.append((key, self.freqDict[key]))
        # Sort by the 1st element of the tuple, the frequency
        self.freqList.sort(key=lambda x: x[1], reverse=True)
        return

    def evaluateWord(self, word):
        # Evaluate if the word should be there
        flag = 1
        if word.lower() in self.omit:
            flag = 0
        return flag


class docHandler:

    def __init__(self, disease, num_articles):
        # Configure web interface
        self.opener = build_opener(HTTPHandler)
        self.headers = 'Mozilla/5.0 (X11; Linux x86_64; rv:27.0) Gecko/20100101 Firefox/27.0'
        self.search_base_url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?'
        self.fetch_base_url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?'
        # Variables
        self.disease = disease
        self.num_articles = num_articles
    ##### UIDS #####

    def get_uids(self):
        retmode = "json"
        db = "pubmed"
        term = self.disease
        retmax = self.num_articles
        url = self.search_base_url + "db=" + db + "&term=" + term + "&retmax=" + retmax + "&retmode=" + retmode

        err_msg = ' [-] Request failed'
        try:
            print(" [+] Getting IDs of documents related to " + term + "...")
            # print(' [+] Requesting %s' % url)

            req = Request(url, headers={'User-Agent': self.headers})
            hdl = self.opener.open(req)
            data = hdl.read()
            return self.parse_uids(data)

        except Exception as err:
            print(err_msg + ': %s' % err)
            return None

    def parse_uids(self, json_data):
        parsed_uids = ""
        # Decode to utf-8
        parsed = json_data.decode("utf-8")
        # Then to string
        d = json.JSONDecoder()
        parsed = d.decode(parsed)
        # Extract UIDs and format them for the url
        uids = parsed['esearchresult']['idlist']
        for uid in uids:
            parsed_uids += uid + ","
        parsed_uids = parsed_uids[:-1]
        return parsed_uids

    ##### ABSTRACTS #####

    def get_abstracts(self, uids):
        db = "pubmed"
        rettype = "abstract"
        retmode = "xml"
        url = self.fetch_base_url + "db=" + db + "&rettype=" + rettype + "&retmode=" + retmode + "&id=" + uids

        err_msg = ' [-] Request failed'
        try:
            print(" [+] Fetching abstracts...")
            # print(' [+] Requesting %s' % url)

            req = Request(url=url, headers={'User-Agent': self.headers})
            hdl = self.opener.open(req)
            data = hdl.read()
            return self.parse_abstracts(data)

        except Exception as err:
            print(err_msg + ': %s' % err)
            return None

    def parse_abstracts(self, abstracts):
        print(" [+] Parsing abstracts...")
        abstract_text = []
        # Decode from byte to string
        abstract = abstracts.decode("utf-8")
        root = ET.fromstring(abstract)
        for node in root.findall(".//Abstract"):
            abstract_text.append(["".join(node.itertext())])
        return abstract_text


# Main program
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host = '127.0.0.1', port = port)
