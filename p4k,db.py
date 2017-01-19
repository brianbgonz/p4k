import p4k
import time
import pickle
import urllib2
import psycopg2

# python 2.7

DBNAME = "p4kdb"
USER = "briangonzalez"
LOGFILE = "log.txt"
FAILUREFILE = "failures.txt"

def builddb(idrange):
    """
    IN:
    list<int> -- idrange -- indices of reviews to be added to db
    """

    # get urls from pickle file
    urls = get_urls()
    for idx in idrange:
        try:
            r = p4k.scrape_review_url(urls[idx])
            add_review_to_db(r)
            print idx, r.less()
            with open(LOGFILE, "a") as f:
                f.write("{} {}\n".format(idx, r.id()))
            
        except urllib2.URLError as e:
            print e
            with open(FAILUREFILE, "a") as f:
                f.write(",{}".format(idx))
        finally:
            time.sleep(6)

    print "DONE"

def get_urls():
    return pickle.load(open('review-urls.p', 'rb'))

def get_review(urls, k):
    return p4k.scrape_review_url(urls[k])

def add_review_to_db(r):
    """
    Review -- r -- review to be added to database.
    updates tables Review, LinkedReview, LinkedArtist in p4kdb database
    """

    add_review = ("INSERT INTO Review "
                  "(id, review_url, artist_url, second_artist_url, "
                  "artist, second_artist, album, year, second_year, "
                  "label, second_label, genre, "
                  "review_header, review_body, author, date, score, bnm) "
                  "VALUES "
                  "(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ")

    data_review = (r.id(), r.review_url(), r.artist_url(), 
                   r.second_artist_url(), r.artist(), 
                   r.second_artist(), r.album(), r.year(), 
                   r.second_year(), r.label(), r.second_label(), 
                   r.genre(), r.review_header(), r.review_body(), 
                   r.author(), r.date(), r.score(), r.bnm())

    add_linked_review = ("INSERT INTO LinkedReview "
                         "(id, linked_review_url) "
                         "VALUES "
                         "(%s,%s) ")

    add_linked_artist = ("INSERT INTO LinkedArtist "
                         "(id, linked_artist_url) "
                         "VALUES "
                         "(%s,%s) ")

    # todo: use cur.statusmessage to check if success?
    with psycopg2.connect(dbname=DBNAME, user=USER) as conn:
        with conn.cursor() as cur:
            # insert into Review table
            cur.execute(add_review, data_review)
            # insert into LinkedReview, LinkedArtist tables
            for linked_review in r.linked_reviews():
                cur.execute(add_linked_review, (r.id(), linked_review))
            for linked_artist in r.linked_artists():
                cur.execute(add_linked_artist, (r.id(), linked_artist))
            
    

if __name__ == "__main__":
    # 17664, 1365-no-more-shall-we-part does not exist
    #idrange = range(17665, 18310)
    builddb(idrange)
