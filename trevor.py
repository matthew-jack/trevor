# Matthew Jack

import sys
import json
import argparse
import xml.etree.ElementTree as ET
from urllib.request import HTTPHandler, Request, build_opener

def main():
    # Options
    parser = argparse.ArgumentParser(description='Visualize common langauge across pathological research')
    parser.add_argument('-c', '--count', action='store', help='limit the number of articles crawled (1-10000)',
                        default=50)
    parser.add_argument("disease", type=str, help='specify which disease to crawl for')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.0')
    args = parser.parse_args()

    # Start it up
    handler = docHandler()
    # Get UIDs of the documents we want
    uids = handler.get_uids(args.disease)
    # Format the data to be traversed
    abstracts = handler.get_abstracts(uids)
    # Calculate word frequencies
    indexer = traverseText(abstracts)
    index = indexer.buildWordIndex()
    # Create data visualization
    viz = dataViz(index)
    viz.populateJSON()
    # Done!
    print(" [#] Complete.")

    return 0

class dataViz:

    def __init__(self, index):
        self.index = index
        self.sizeFactor = 625

    def populateJSON(self):
        print(" [+] Generating visualization...")
        # Create JSON skeleton
        skeleton = self.createJSONSkeleton()
        master = {}
        jsonString = "{ \"name\": \"Visual Medicine\",\"children\": [ "
        # Generate the JSON visualization data
        j = 0
        for parent in skeleton:
            j += 1
            i = 0
            temp = list()
            while i < len(parent):
                temp.append(dict(name=parent[i][0], size=int(parent[i][1])*self.sizeFactor))
                i += 1
            master.update(name=parent[0][0], children=temp)
            if j < len(skeleton):
                jsonString = jsonString + json.dumps(master, indent=3) + ", "
            else:
                jsonString = jsonString + json.dumps(master, indent=3) + " ] }"
        # Write to file
        f = open('python_output.json', 'w')
        f.write(jsonString)
        f.close()
        return

    def createJSONSkeleton(self):
        # Start from element 1, if it's the same size, append it to a list.
        # if it's bigger, start a new list
        skeleton = []
        currentList = []
        currentList.append(self.index[0])
        i = 1
        while i < len(self.index):
            # To avoid out-of-bounds stuff
            if i == (len(self.index) - 1):
                if self.index[i][1] == self.index[i-1][1]:
                    currentList.append(self.index[i])
                else:
                    skeleton.append(currentList[:])
                    currentList = list()
                break

            if self.index[i+1][1] > self.index[i][1]:
                skeleton.append(currentList[:])
                currentList = list()
            else:
                currentList.append(self.index[i])
            i += 1
        # Get rid of pesky empty lists
        skeleton = [x for x in skeleton if x]
        return skeleton

class traverseText:
    # Algorithm:
    # - Create a dictionary of unspecified size
    # - Increment dict[word] by 1 each time word is encountered
    # --- if dict[word] does not exist, create it and set it to 1
    # - Sort, print.

    def __init__(self, text):
        # Using a dict initiatlly because
        # it's easy to stick a value in a key
        self.text = text
        self.freqDict = dict()
        self.freqList = []
        self.omit = self.loadOmitWords("omit_words")

    def loadOmitWords(self, filename):
        omit = []
        f = open(filename, 'r')
        words = f.read()
        for word in words.split():
            omit.append(word)
        return omit

    def buildWordIndex(self):
        print(" [+] Building index...")
        for paper in self.text:
            # Now we're in a list that holds one abstract
            for word in paper:
                # Now it's a string
                for word in word.split():
                    # Down to words
                    if word not in self.omit:
                        if (word != '') and (not word.isspace()) and (word is not None):
                            if not word.isnumeric():
                                if word.isalnum():
                                    if word not in self.freqDict:
                                        self.freqDict[word] = 1
                                    else:
                                        self.freqDict[word] += 1
        return self.sortWordIndex()

    def sortWordIndex(self):
        for key in self.freqDict:
            self.freqList.append((key, self.freqDict[key]))
        # Sort by the 1st element of the tuple, the frequency
        self.freqList.sort(key=lambda x: x[1])
        return self.freqList

class docHandler:

    def __init__(self):
        # Configure web interface
        self.opener = build_opener(HTTPHandler)
        self.headers = 'Mozilla/5.0 (X11; Linux x86_64; rv:27.0) Gecko/20100101 Firefox/27.0'
        self.search_base_url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?'
        self.fetch_base_url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?'

    ##### UIDS #####

    def get_uids(self, disease):
        db = "pubmed"
        term = disease.replace("'","\'")
        retmax = "10"
        retmode = "json"
        url = self.search_base_url + "db=" + db + "&term=" + term + "&retmax=" + retmax + "&retmode=" + retmode

        err_msg = ' [-] Request failed'
        try:
            print(" [+] Getting IDs of documents related to " + term + "...")
            print(' [+] Requesting %s' % url)

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
            print(' [+] Requesting %s' % url)

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
if __name__ == "__main__":
    sys.exit(main())
