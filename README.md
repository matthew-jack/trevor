# Trevor - A Medical Data Visualization Tool


There is an unprecedentedly large pool of medical research available to the general public, which gives anyone the chance to view, analyze, and play with real clinical data. Without extensive medical training, however, it's difficult to learn a wide breadth of information from articles alone, but looking at the big picture — and the way topics overlap — can make it easier.

Enter a disease into Trevor and see the most prevalent language observed across published research. The goal is to connect similar data points across topics like diseases, genetic mutations, or even genetic toxicology correlation data.

Live on Heroku at https://trevor-web.herokuapp.com/



### Version
v1.0 :tada: - full web app release; still little/bad error handling, lack of features and polish

#### Todo
* Add support for multiple crawl queries
* Add error/exception handling
* BUG FIXES!!!!!!111!

### Libraries

Trevor is written in Python 3 using the Flask web app microframework, and the D3.js library for data visualization. JSON data required by D3.js is generated in Python and written to disk with an accompanying HTML page.


### Installation

A standard Python3 installation should work fine. This is how it runs:

```sh
$ python3 trevor.py 
```

Then watch for the server and port to visit. 


----------
#### @matthewmjack / matthew-jack@uiowa.edu
