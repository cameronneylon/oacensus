__author__ = 'cneylon'
from oacensus.scraper import ArticleScraper
from oacensus.models import Article
from oacensus.models import Repository
from oacensus.models import Instance
import json
import requests
import xml.etree.ElementTree as ET
import time

class CORE(ArticleScraper):
    """
    Gets accessibility information for articles with DOIs in the database.
    """
    aliases = ['core']

    _settings = {
            'base-url' : ("Base url of CORE API", "http://core.kmi.open.ac.uk/api/"),
            'api-call' : ("Type of API Call to CORE", 'search'),
            'api-key' : ("CORE API Key, see http://core.kmi.open.ac.uk/api/doc", '1FLubv1AaE3S13OuWQtZeRF208LPP1cS'),
            'api-delay': ("Delay to add between API calls in seconds", 1)
            }

    def scrape(self):
        # don't use scrape method since our query depends on db state, so
        # caching will not be accurate
        pass

    def process(self):
        articles = Article.select().where(~(Article.title >> None))
        for article in articles:
            query = article.title
            try:
                response = self.core_request(query)
                response.raise_for_status()
            except requests.exceptions.HTTPError:
                if response.status_code == 500:
                    print 'Core Internal Error', response.status_code
                    continue
            core_response = ET.fromstring(response.text.encode('utf-8'))
            repo, url, ftr = self.core_process(core_response, article.title)
            if repo:
                Instance.create(article = article,
                            repository = repo,
                            free_to_read = ftr,
                            info_url=url,
                            source=self.db_source(),
                            log='Core response matched to article title')


    def core_request(self, query):
        baseurl = "%s%s/" % (self.setting('base-url'), self.setting('api-call'))
        response = requests.get((baseurl+query), params = {'api_key' : self.setting('api-key')})
        time.sleep(self.setting('api-delay'))
        return response

    def core_process(self, core_response, title):
        metadata_elems = core_response.find('record').find('metadata').find('{http://www.openarchives.org/OAI/2.0/oai_dc/}dc')
        if metadata_elems.find('{http://purl.org/dc/elements/1.1/}title').text == title:
            reponame = 'core'

            for identifier in metadata_elems.iter('{http://purl.org/dc/elements/1.1/}identifier'):
                if identifier.text.startswith('http://core.kmi.open.ac.uk/download/pdf/'):
                    url = identifier.text
                    ftr = True
                    repository = Repository.find_or_create_by_name({'name':reponame,
                                                            'source': 'core',
                                                            'log' : 'Created by core plugin'})
                    return repository, url, ftr

        else:
            return False, False, False