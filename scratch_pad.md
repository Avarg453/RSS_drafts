## scratchpad

# First from each source get an average of how many new articles per day

Maybe at first just do all new articles past three days

# Estimate token cost and how I'd be able to send entire article context (probably some filtering needed to go from html down to just the article body

Some suggest Gemma 2 or Granite3.2 for the text summarization

# Ollama for running granite model

<https://huggingface.co/ibm-granite/granite-3.2-2b-instruct>

<https://www.youtube.com/watch?v=0NJEoIqQILE>

<https://www.ralgar.one/ollama-on-windows-a-beginners-guide/>

DN test notes
contents:
    '''
    dn_feed=feedparser.parse("<https://www.dropsitenews.com/feed>")

    for elem in dn_feed.entries:
        print(elem.title)
    '''

We have the entry contents being spit out but the text is all split up:

[{'base': 'https://www.thebignewsletter.com/feed',
  'language': None,
  'type': 'text/html',
  'value': '<p><em>&#8220;The France family and NASCAR are monopolistic '
           'bullies. And bullies will continue to impose their will to hurt '
           'others until their targets stand up and refuse to be victims. That '
           'moment has now arrived.&#8221; - <a '
           'href="https://storage.courtlistener.com/recap/gov.uscourts.ncwd.117501/gov.uscourts.ncwd.117501.107.0.pdf">complaint '
           'against NASCAR</a></em></p><p>On Monday in a Charlotte, North '
           'Carolina courthouse, the weirdest and most interesting '
           'monopolization trial of the year started. A driving team, 23XI '
           'Racing, is suing NASCAR over its control of the sport, alleging

html2text seems to work fine:

test_article=rss_feed.entries[0]['content'][0]['value']

import html2text

h = html2text.HTML2Text()

print(h.handle(test_article))

Need to handle things like images embedded:
[![](https://substackcdn.com/image/fetch/$s_!tGz_!,w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-
post-
media.s3.amazonaws.com%2Fpublic%2Fimages%2Fed3ad900-da74-48aa-9314-7cb3ea395798_1012x681.png)](https://substackcdn.com/image/fetch/$s_!tGz_!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-
post-
media.s3.amazonaws.com%2Fpublic%2Fimages%2Fed3ad900-da74-48aa-9314-7cb3ea395798_1012x681.png)

and embedded links:
_" The France family and NASCAR are monopolistic bullies. And bullies will
continue to impose their will to hurt others until their targets stand up and
refuse to be victims. That moment has now arrived." \- [complaint against
NASCAR](https://storage.courtlistener.com/recap/gov.uscourts.ncwd.117501/gov.uscourts.ncwd.117501.107.0.pdf)_

# Next steps

# # Figure out nosql or some other kind of straight forward enough db to store all of the entries for

Dropsite - <https://www.dropsitenews.com/feed>

Bolts Mag - <https://boltsmag.org/feed/>

Big (jeff stoller) - <https://www.thebignewsletter.com/feed>

Counterpunch - <https://www.counterpunch.org/feed/>

Truthout - <https://truthout.org/feed/>

Jacobin (LATAM) - <https://jacobinlat.com/feed/>

Ken Klippenstein - <https://www.kenklippenstein.com/feed>

# # Is there a quick programattic way to ensure that entry value contains majority of the articl econtents?

# # Neeed to derive some kind of ID for each of these articles

- source website-date (YYYYMMDD)?-AbbrevTitle
- ID NUM for website - YYYYMMDD - ID for entry that day??

# # we have a corpus of ~250 articles, ignoring the ones in spanish for now (can potentially use langdetect to add an element for language in the json)

# extractive summarization

spaCy: A Python library for NLP tasks.
PyTextRank: A spaCy extension that implements the TextRank algorithm.

# abstractive summarization

PEGASUS: A Transformer Model for Text Summarization
PEGASUS is a Transformer-based model designed specifically for text summarization. Unlike other models, PEGASUS uses a unique pre-training strategy where critical sentences are masked during training. The model is then tasked with generating these hidden sentences, which enables it to create more accurate and coherent summaries.

To use the PEGASUS model for text summarization, you need to install the following libraries and frameworks:

'''
!pip install git+<https://github.com/Lightning-AI/pytorch-lightning>
!pip install git+<https://github.com/huggingface/transformers>
!pip install sentencepiece
!pip install git+<https://github.com/stas00/transformers>
!pip install pegasus
'''

alternatives can be found under x-sum section in <https://nlpprogress.com/english/summarization.html>

there's also doc2vec for potentially highlighting overlap between articles outside of extracted meaningful words or summaries.
<https://medium.com/wisio/a-gentle-introduction-to-doc2vec-db3e8c0cce5e>

For semantic similarity between words there is also WordNet
Python
Natural Language Toolkit has taken over the development of pywordnet. There is now a Python package, nltk_lite.wordnet, which incorporates pywordnet and which supports WordNet 2.1. It is included in NLTK Lite.

BabelNet is a very large multilingual lexical database, developed by Roberto Navigli  [email] , Simone Paolo Ponzetto and others at the University of Rome "La Sapienza" in the context of the ERC Starting Grant MultiJEDI. BabelNet provides a wide-coverage knowledge repository in which WordNet is automatically aligned to the English Wikipedia, and lexicalizations for its concepts (i.e. English Wikipedia pages and WordNet synsets) are provided on the basis of Wikipedia cross-language links and the output of a machine translations system. The current version, which is freely available under a Creative Commons license, comprises a network of more than 3 million synsets and 70 millions semantic relations, and it can also be browsed through an on-line interface.
The Global WordNet Association is a free, public and non-commercial organization that provides a platform for discussing, sharing and connecting wordnets for all languages in the world.
MultiWordNet, developed by Luisa Bentivogli [email] and others is a multilingual lexical database, developed at ITC-irst, in which the Italian WordNet is strictly aligned with Princeton WordNet 1.6. The current version includes around 44,400 Italian lemmas organized into 35,400 synsets which are aligned, whenever possible, with their corresponding English Princeton synsets. The MultiWordNet database can be freely browsed through its on-line interface, and is distributed both for research and commercial use. Information on the distribution licence is available at the web site.
The Open Multilingual WordNet is a massively multilingual database that links many different WordNet projects, developed by Francis Bond [email] at Nanyang Technological University.  It currently links open-source wordnets in over 20 languages, and allows you to both look words up online or download the data.
