## scratchpad:

# First from each source get an average of how many new articles per day

Maybe at first just do all new articles past three days


# Estimate token cost and how I'd be able to send entire article context (probably some filtering needed to go from html down to just the article body

Some suggest Gemma 2 or Granite3.2 for the text summarization


# Ollama for running granite model

https://huggingface.co/ibm-granite/granite-3.2-2b-instruct

https://www.youtube.com/watch?v=0NJEoIqQILE

https://www.ralgar.one/ollama-on-windows-a-beginners-guide/







DN test notes
contents:
    '''
    dn_feed=feedparser.parse("https://www.dropsitenews.com/feed")

    for elem in dn_feed.entries:
        print(elem.title)
    '''

# PS C:\Users\avarg\Documents\ProgPlayground\RSS_drafts> py .\feedparser_script.py
# Child Amputees in Gaza Use Makeshift Prosthetics as Israel Restricts Medical Supplies
# Jeffrey Epstein Aided Alan Dershowitz’s Attack on Mearsheimer and Walt’s “Israel Lobby”
# Gaza faces more winter storms; RSF declares “truce” in Sudan after genocidal killing spree; Trump to reassess all Biden refugees
# A Single Warehouse in Jersey City Moved Over A Thousand Tons of Military Cargo to Israel Every Week
# Hezbollah commander killed in Israeli airstrike; U.S. reportedly readies for covert action in Venezuela; Musk's DOGE quietly dissolves
# Weapons of Willpower: Hamas and Islamic Jihad on Trump's Gaza Plan
# Darfur's governor said 27,000 killed over three days last month; U.S. pushes Ukraine to give up Donbas region to end the war with Russia
# “Modi on board”: Jeffrey Epstein Pressed Steve Bannon to Meet With Indian PM Shortly Before His Death
# Israel Kills Over 30 Palestinians in Gaza in One of Bloodiest Assaults of "Ceasefire"
# Israeli forces extend "red zone" further into Gaza City; Mamdani retains controversial NYPD commissioner Jessica Tisch
# Andrew Garroni Arrested for Alleged “Massive Fraud Scheme” After Drop Site Investigation
# U.S. Mercenary Firm Tied to Notorious Aid Scheme Is Recruiting for New Gaza Deployment
# Israeli airstrike on Palestinian refugee camp in Lebanon kills 13; Congress approves release of Epstein files
# Trump, the “Peace President,” Continues Endless American Wars
# Jeffrey Epstein Pursued Swiss Rothschild Bank to Finance Israeli Cyberweapons Empire
# Poland Repurposed a Nazi Factory Site to Make TNT to Drop on Gaza
# UN Security Council approves Trump's Gaza plan; Israel vows to block any path to a Palestinian state
# UN Security Council faces major vote on Gaza; Trump caves on Epstein vote; Israeli attacks on Lebanon and Gaza
# Euphrates River Becomes the Last Battle Line in Syria’s Civil War
# Tents in Gaza Collapse From Rain as Palestinians Struggle With Massive Flooding
# PS C:\Users\avarg\Documents\ProgPlayground\RSS_drafts> py .\feedparser_script.py
# Child Amputees in Gaza Use Makeshift Prosthetics as Israel Restricts Medical Supplies
# Jeffrey Epstein Aided Alan Dershowitz’s Attack on Mearsheimer and Walt’s “Israel Lobby”
# Gaza faces more winter storms; RSF declares “truce” in Sudan after genocidal killing spree; Trump to reassess all Biden refugees
# A Single Warehouse in Jersey City Moved Over A Thousand Tons of Military Cargo to Israel Every Week
# Hezbollah commander killed in Israeli airstrike; U.S. reportedly readies for covert action in Venezuela; Musk's DOGE quietly dissolves
# Weapons of Willpower: Hamas and Islamic Jihad on Trump's Gaza Plan
# Darfur's governor said 27,000 killed over three days last month; U.S. pushes Ukraine to give up Donbas region to end the war with Russia
# “Modi on board”: Jeffrey Epstein Pressed Steve Bannon to Meet With Indian PM Shortly Before His Death
# Israel Kills Over 30 Palestinians in Gaza in One of Bloodiest Assaults of "Ceasefire"
# Israeli forces extend "red zone" further into Gaza City; Mamdani retains controversial NYPD commissioner Jessica Tisch
# Andrew Garroni Arrested for Alleged “Massive Fraud Scheme” After Drop Site Investigation
# U.S. Mercenary Firm Tied to Notorious Aid Scheme Is Recruiting for New Gaza Deployment
# Israeli airstrike on Palestinian refugee camp in Lebanon kills 13; Congress approves release of Epstein files
# Trump, the “Peace President,” Continues Endless American Wars
# Jeffrey Epstein Pursued Swiss Rothschild Bank to Finance Israeli Cyberweapons Empire
# Poland Repurposed a Nazi Factory Site to Make TNT to Drop on Gaza
# UN Security Council approves Trump's Gaza plan; Israel vows to block any path to a Palestinian state
# UN Security Council faces major vote on Gaza; Trump caves on Epstein vote; Israeli attacks on Lebanon and Gaza
# Euphrates River Becomes the Last Battle Line in Syria’s Civil War
# Tents in Gaza Collapse From Rain as Palestinians Struggle With Massive Flooding



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


# Next steps:
# # Figure out nosql or some other kind of straight forward enough db to store all of the entries for 

Dropsite - https://www.dropsitenews.com/feed

Bolts Mag - https://boltsmag.org/feed/

Big (jeff stoller) - https://www.thebignewsletter.com/feed

Counterpunch - https://www.counterpunch.org/feed/

Truthout - https://truthout.org/feed/

Jacobin (LATAM) - https://jacobinlat.com/feed/

Ken Klippenstein - https://www.kenklippenstein.com/feed

# # Is there a quick programattic way to ensure that entry value contains majority of the articl econtents?

# # Neeed to derive some kind of ID for each of these articles
- source website-date (YYYYMMDD)?-AbbrevTitle
- ID NUM for website - YYYYMMDD - ID for entry that day??