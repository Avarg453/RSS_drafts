import feedparser
import html2text
import json
from urllib.parse import urlparse
import os

from pathlib import Path

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

        entry_data['Source']=entrylinkcomp

        entry_data['link']=entry['link']

        entry_data['title']=entry['title']

        entry_data['author']=entry['author']

        entry_data['content']=h.handle(entry['content'][0]['value'])

        json_data = json.dumps(entry_data, indent=4)

        with open(f"./json_dump/{uniq_ID}.json", "w") as f:
            f.write(json_data)


# function to update existing json files with new property keys that have been added since they were pulled, if information is available inside the json
for json_file in os.listdir('json_dump'):
    # add "Source" key if missing using the substring in UID before first hyphen
    with open(Path('json_dump') / json_file, 'r', encoding='utf-8') as f:
        data = json.load(f) 
        # check if data contains Source key
        if 'Source' not in data:
            source_value = data['uID'].split('-')[0]
            data['Source'] = source_value
        # save the udpated json back to file
    with open(Path('json_dump') / json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
        # if amount of updated files greater than 10, print total count of files that were updated
        # otherwise just print each file that was updated