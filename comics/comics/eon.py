from comics.aggregator.crawler import PondusNoCrawlerBase
from comics.meta.base import MetaBase

class Meta(MetaBase):
    name = 'EON'
    language = 'no'
    url = 'http://www.pondus.no/'
    start_date = '2008-11-19'
    rights = 'Lars Lauvik'

class Crawler(PondusNoCrawlerBase):
    schedule = 'Mo,Tu,We,Th,Fr,Sa,Su'

    def crawl(self, pub_date):
        return self.crawl_helper('20058')
