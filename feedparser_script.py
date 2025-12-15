import feedparser
import html2text
import json
from urllib.parse import urlparse
import os

h = html2text.HTML2Text()

# list of rss feeds to parse
rss_feed_list=[
    "https://boltsmag.org/feed/",
    "https://www.thebignewsletter.com/feed",
    "https://www.counterpunch.org/feed/",
    "https://jacobinlat.com/feed/", 
    "https://www.kenklippenstein.com/feed", 
    "https://zeteo.com/feed", 
    "https://www.leefang.com/feed", 
    "https://www.propublica.org/feed", 
    "https://mexicosolidarity.com/feed/", 
    "https://www.compactmag.com/feed/"
]

os.makedirs('json_dump', exist_ok=True)

for feed in rss_feed_list:
    rss_feed=feedparser.parse(feed)
    for entry in rss_feed.entries:
        entry_data={}


        datelist=[]
        datetuple=entry['published_parsed'][0:6]
        for elem in datetuple:
            datelist.append(str(elem))
        entrydatecomp='-'.join(datelist) 
        entrylinkcomp=max(urlparse(entry['link']).netloc.split('.'), key=len)
        # line above is taking the main domain chunk and splitting on the . presumably 
        # after www and before com/org/net and then sorting that list based on length
        # since domain will most likely just be the max length thing anyways
        
        uniq_ID=entrylinkcomp+'-'+entrydatecomp

        entry_data['uID']=uniq_ID

        entry_data['link']=entry['link']

        entry_data['title']=entry['title']

        entry_data['author']=entry['author']

        entry_data['content']=h.handle(entry['content'][0]['value'])

        json_data = json.dumps(entry_data, indent=4)

        with open(f"./json_dump/{uniq_ID}.json", "w") as f:
            f.write(json_data)

# for key in rss_feed:
#     if type(rss_feed[key]) is dict:
#         for subkey in rss_feed[key]:
#             print(f"for {key}:{subkey}:{len(rss_feed[key][subkey])}")
#     elif type(rss_feed[key]) is list:
#         print(f"for {key}:{len(rss_feed[key])}")
#     else:
#         print(f"{key} is type: {type(rss_feed[key])}")
