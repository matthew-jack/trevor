# Trevor - A Medical Data Visualization Tool


There is an unprecedentedly large pool of medical research available to the general public, which gives anyone the chance to view, analyze, and play with the data. Without extensive medical training, however, it's difficult to learn a wide breadth of information from articles alone, but looking at the big picture — and they way it interacts — can make it easier.

Enter a disease into Trevor and see the most prevalent language observed across published research. The goal is to connect similar data points across topics like diseases, genetic mutations, or even genetic toxicology correlation data.



### Version
0.1b - incomplete and buggy; full release planned

#### Todo
* Add support for multiple crawl queries
* Get parseargs up and running
* Add error/exception handling
* BUG FIXES!!!!!!111!

### Libraries

Trevor is written in Python 3 and uses the D3.js library for data visualization. JSON data required by D3.js is generated in Python and written to disk with an accompanying HTML page.


### Installation

A standard Python3 installation should work fine. This is how it runs:

```sh
$ python3 trevor.py "celiac disease"
```

```sh
usage: trevor.py [-h] [-c COUNT] [-v] disease
Visualize common langauge across pathological research

positional arguments:
  disease               specify which disease to crawl for

optional arguments:
  -h, --help            show this help message and exit
  -c COUNT, --count COUNT
                        limit the number of articles crawled (1-10000)
  -v, --version         show program's version number and exit
```

----------
#### @matthewmjack / matthew-jack@uiowa.edu