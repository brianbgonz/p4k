import urllib2
import datetime
import re
from bs4 import BeautifulSoup
from collections import OrderedDict

# python 2.7

URL_SITEMAP_REVIEWS = 'http://pitchfork.com/sitemap-album-reviews.xml'

class Review:
    """
    Review
    IN:
    string -- url -- url address of review page
    BeautifulSoup -- soup -- from xml of review page
    """

    def __init__(self, url, soup):
        self.url = url
        self.soup = soup

    def __unicode__(self):
        if self.bnm():
            if self.second_year():
                bestnew = "BNR"
            else:
                bestnew = "BNM"
        else:
            bestnew = ""

        s = []
        fmt = u'Review url: {}\nid: {}\n'
        s.append(fmt.format(self.url, self.id()))

        fmt = u'Artist url: {}\n'
        s.append(fmt.format('\n'.join(self.all_artist_urls())))

        fmt = u'Artist: {}\nAlbum: {}\n'
        s.append(fmt.format(' / '.join(self.all_artists()), self.album()))

        fmt = u'Label: {}\nYear: {}\nGenre: {}\n'
        s.append(fmt.format(' / '.join(self.all_labels()),
                            '/'.join([str(x) for x in self.all_years()]), 
                            self.genre()))

        fmt = u'Author: {}\nDate: {}\nScore: {:.1f} {}\n'
        s.append(fmt.format(self.author(), self.date().strftime('%Y-%m-%d'),
                            self.score(), bestnew))

        fmt = u'Linked artists:\n{}\n'
        s.append(fmt.format('\n'.join(self.linked_artists())))

        fmt = u'Linked reviews:\n{}\n'
        s.append(fmt.format('\n'.join(self.linked_reviews())))
        
        return ''.join(s)

    def __str__(self):
        return unicode(self).encode('utf-8')

    def less(self):
        """
        print less
        """
        s = u'{} / {}'.format(self.artist(), self.album())
        return unicode(s).encode('utf-8')

    def all_artists(self):
        """
        OUT:
        list<string> -- artist names
        """
        artist_tag = self.soup.find(class_='artist-list').find_all("li")
        return [x.get_text() for x in artist_tag]

    def artist(self):
        """
        OUT:
        string -- artist name
        """
        artist_tag = self.soup.find(class_='artist-list').find_all("li")
        return artist_tag[0].get_text()

    def second_artist(self):
        """
        OUT:
        string -- second artist name if exists, else None
        """
        artist_tag = self.soup.find(class_='artist-list').find_all("li")
        return artist_tag[1].get_text() if len(artist_tag) > 1 else None

    def album(self):
        """
        OUT:
        string -- album name
        """
        return self.soup.find(class_='review-title').get_text()

    def all_labels(self):
        """
        OUT:
        list<string> -- record label names
        
        todo: return None for self-released (eg, Chance?)
        """
        label_tag = self.soup.find(class_='label-list').find_all("li")
        return [x.get_text() for x in label_tag]

    def label(self):
        """
        OUT:
        string -- record label name
        """
        label_tag = self.soup.find(class_='label-list').find_all("li")
        return label_tag[0].get_text() if len(label_tag) > 0 else None

    def second_label(self):
        """
        OUT:
        string -- second record label name if exists, else None
        """
        label_tag = self.soup.find(class_='label-list').find_all("li")
        return label_tag[1].get_text() if len(label_tag) > 1 else None

    def all_years(self):
        """
        OUT:
        list<int> -- album (re)release year(s)
        """
        year_raw = self.soup.find(class_='year').contents[4]
        return [int(x) for x in year_raw.split('/') if x.isdigit()]

    def year(self):
        """
        OUT:
        int -- album release year
        """
        year_raw = self.soup.find(class_='year').contents[4].split('/')
        if len(year_raw) > 0 and year_raw[0].isdigit():
            return int(year_raw[0])
        else:
            return None

    def second_year(self):
        """
        OUT:
        list<int> -- album re-release year
        """
        year_raw = self.soup.find(class_='year').contents[4].split('/')
        if len(year_raw) > 1 and year_raw[1].isdigit():
            return int(year_raw[1])
        else:
            return None

    def genre(self):
        """
        OUT:
        string or None -- album genre
        """
        genre_tag = self.soup.find(class_='genre-list')
        return genre_tag.get_text() if genre_tag else None

    def score(self):
        """
        OUT:
        float or None -- review score from 0.0 to 10.0
        """
        score_tag = self.soup.find(class_='score')
        return float(score_tag.get_text()) if score_tag else None

    def bnm(self):
        """
        OUT:
        bool -- True if Best New Music or Best New Reissue, else False
        """
        return bool(self.soup.find(class_='bnm'))

    def review_header(self):
        """
        OUT:
        string -- body of text in review header
        """
        return self.soup.find(class_='abstract').get_text()

    def review_body(self):
        """
        OUT:
        string -- body of text in review body
        """
        return self.soup.find(class_='contents').get_text()

    def author(self):
        """
        OUT:
        string -- author of review
        """
        return self.soup.find(class_='display-name').get_text()

    def date(self):
        """
        OUT:
        datetime.datetime -- date of review publication

        todo: maybe switch this to a datetime.date?
        """
        date_tag = self.soup.find(class_='pub-date').get('title')
        return datetime.datetime.strptime(' '.join(date_tag.split(' ')[:4]),
                                          '%a %b %d %Y')

    def id(self):
        """
        OUT:
        int -- unique(?) identifier of review, taken from url
        """
        return int(float(self.url.split('-')[0].split('/')[-1]))

    def review_url(self):
        """
        OUT:
        string -- url address of this review
        """
        return self.url

    def all_artist_urls(self):
        """
        OUT:
        list<string> -- url addresses to artist pages
        """
        artist_tag = self.soup.find(class_='artist-links').find_all("a")
        return ['http://pitchfork.com' + x.get("href") for x in artist_tag]

    def artist_url(self):
        """
        OUT:
        string -- url address to artist page
        """
        artist_tag = self.soup.find(class_='artist-links').find_all("a")
        if len(artist_tag) > 0:
            return 'http://pitchfork.com' + artist_tag[0].get("href")
        else:
            return None

    def second_artist_url(self):
        """
        OUT:
        string -- url address to second artist page
        """
        artist_tag = self.soup.find(class_='artist-links').find_all("a")
        if len(artist_tag) > 1:
            return 'http://pitchfork.com' + artist_tag[1].get("href")
        else:
            return None

    def links(self):
        """
        OUT:
        list<string> -- url addresses of sites linked to in review body
        """
        links_tag = self.soup.find(class_='contents').find_all("a")
        a = [x.get("href") for x in links_tag]
        # remove duplicates
        return list(OrderedDict.fromkeys(a))

    def linked_artists(self):
        """
        OUT:
        list<string> -- url addresses of artist pages linked to in review body
        """
        p = re.compile('^http://pitchfork.com/artists/.*')
        return [p.match(x).group() for x in self.links() if x and p.match(x)]

    def linked_reviews(self):
        """
        OUT:
        list<string> -- url addresses of other reviews linked to in review body
        """
        p = re.compile('^http://pitchfork.com/reviews/albums/.*')
        return [p.match(x).group() for x in self.links() if x and p.match(x)]

def get_review_urls(xmlfile='sitemap-album-reviews.xml'):
    """
    IN:
    string -- xmlfile -- XML file of sitemap with album reviews
    OUT:
    list<string> -- url addresses of all album reviews
    """
    with open(xmlfile, 'r') as f:
        xmltext = f.read()

    soup = BeautifulSoup(xmltext, 'lxml')
    return [x.get_text() for x in soup.find_all('loc')]

def scrape_review_url(url):
    """
    IN: 
    string -- url -- url address of album review
    OUT:
    Review -- object for that review with methods to get artist etc.

    Etiquette: try not to call more than six times a minute I guess?
    """
    request = urllib2.Request(url=url,
                              data=None,
                              headers={'User-Agent' : 'Mozilla/5.0'})
    try:
        response = urllib2.urlopen(request)
    except urllib2.URLError as e:
        if hasattr(e, 'reason'):
            print 'We failed to reach a server.'
            print 'Reason: ', e.reason
        elif hasattr(e, 'code'):
            print 'The server couldn\'t fulfill the request.'
            print 'Error code: ', e.code
        raise
    else:
        soup = BeautifulSoup(response.read(), 'lxml')
        return Review(url, soup)

def hello():
    """
    todo placeholder
    """
    print "Hello, World!"

if __name__ == "__main__":
    hello()
