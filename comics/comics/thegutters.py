from comics.aggregator.crawler import CrawlerBase, CrawlerImage
from comics.core.comic_data import ComicDataBase


class ComicData(ComicDataBase):
    name = 'The Gutters'
    language = 'en'
    url = 'http://the-gutters.com/'
    rights = 'Blind Ferret Entertainment'


class Crawler(CrawlerBase):
    history_capable_days = 14
    schedule = 'Mo,We,Fr'
    time_zone = 'America/Montreal'

    def crawl(self, pub_date):
        feed = self.parse_feed('http://feeds.feedburner.com/TheGutters')
        for entry in feed.for_date(pub_date):
            url = entry.html(entry.description).src('img[src*="/comics/"]')
            title = entry.title.replace('Gutters: ', '')
            return CrawlerImage(url, title)
