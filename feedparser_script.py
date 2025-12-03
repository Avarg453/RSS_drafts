import feedparser
import pprint

# rss_feed=feedparser.parse("https://www.dropsitenews.com/feed")
rss_feed=feedparser.parse("https://www.thebignewsletter.com/feed")
# rss_feed.keys
# dict_keys(['bozo', 'entries', 'feed', 'headers', 'etag', 'href', 'status', 'encoding', 'version', 'namespaces'])

# rss_feed.entries[0].keys()
# dict_keys(['title', 'title_detail', 'summary', 'summary_detail', 'links', 'link', 'id', 'guidislink', 'authors', 'author', 'author_detail', 'published', 'published_parsed', 'content'])

# rss_feed.entries[0]['title_detail']

# rss_feed.entries[0]['summary_detail']

# rss_feed.entries[0]['link'] # link to article

# rss_feed.entries[0]['published_parsed'] #all of these are ints
#  time.struct_time(tm_year, tm_mon, tm_mday, tm_hour, tm_min, tm_sec, tm_wday, tm_yday, tm_isdst)

# rss_feed.entries[0]['id'] # this might always just be the same as the link

for key in rss_feed:
    if type(rss_feed[key]) is dict:
        for subkey in rss_feed[key]:
            print(f"for {key}:{subkey}:{len(rss_feed[key][subkey])}")
    elif type(rss_feed[key]) is list:
        print(f"for {key}:{len(rss_feed[key])}")
    else:
        print(f"{key} is type: {type(rss_feed[key])}")

# print(rss_feed.entries[0]['title_detail'])

# print(rss_feed.entries[0]['summary_detail'])

# print(rss_feed.entries[0]['link'])

# print(rss_feed.entries[0]['published_parsed'])

# print(rss_feed.entries[0]['id'])



test_article=rss_feed.entries[0]['content'][0]['value']


import html2text

h = html2text.HTML2Text()

print(h.handle(test_article))