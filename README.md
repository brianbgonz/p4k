# Pitchfork reviews analysis
This is very much "in-progress", and mostly a personal learning experience. I switched from Python 2.7 to 3.4 halfway through; I'll eventually go back and get the whole thing up to 3.4.

Some (ill-defined) goals:
- do some regression, see if score can be estimated from other features
- see if a classifier can be built for BNM designation
- build directed graph from artist-to-artist links in review text (maybe some network community detection?)
- try some clustering (k-means on features, or something spectral from adjacency matrix of artist-to-artist links)
- eventually look at text of review body, try to extract some NLP features
- this might be the wrong data set for this, but ultimately I'd like to do some supervised learning of "albums I like" from different sites (RYM, AV Club, CoS, /mu/?) to try to find out more about my own tastes in music. 

Known issues:
- I didn't provide a mechanism for scraping information from multi-album reviews, so the behavior of that data is undefined. It's really only a problem for reissued albums (eg, it counts Weezer's Death to False Metal as a 3.5 Best New Reissue because that review is lumped in with Pinkerton).
- Genres are stored in the db as a single string, eg 'RapPop/R&BElectronic' contains ('Rap', 'Pop/R&B', 'Electronic'). I'm looking into a better way of grouping them.
- My data set only goes up to November 2016. After making sure my old scripts are 3.4-compliant I plan on keeping the db up to date with new reviews.

## p4k.py \ p4k,db.py
I used `BeautifulSoup` to scrape information from all the reviews, and wrote that info to a Postgresql database.
Some of this code is partly inspired by Michal's [unofficial Pitchfork API](https://github.com/michalczaplinski/pitchfork).

## p4k,data.ipynb
Jupyter notebook with some basic analysis of the review data.

## p4k,clustering.ipynb
Jupyter notebook where I'm working on finding some clusters / network community detection.