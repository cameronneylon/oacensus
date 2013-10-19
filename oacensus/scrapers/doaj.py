from bs4 import BeautifulSoup
from oacensus.models import Journal
from oacensus.scraper import Scraper
import re
import requests
import os
import codecs

class DoajJournals(Scraper):
    """
    Scrape journal info from DOAJ website.
    """
    aliases = ['doaj']

    _settings = {
            "base-url" : ("Base url for accessing DOAJ.", "http://www.doaj.org/doaj"),
            'standard-params' : (
                "Params used in every request.",
                {'func' : 'browse', 'uiLanguage' : 'en' }
                )
            }

    def number_of_pages(self):
        """
        Scrape the initial page to determine how many total pages there are.
        """
        print "determining number of pages..."
        result = requests.get(
                self.setting('base-url'),
                params = self.setting('standard-params')
            )

        soup = BeautifulSoup(result.text)

        key = "div.resultLabel table tr td"
        listing = soup.select(key)[1]

        m = re.search("of ([0-9]+)", listing.text)
        assert m is not None
        return int(m.groups()[0])

    def scrape(self):
        n = self.number_of_pages()

        for page_index in range(n):
            print "processing page", page_index+1, "of", n

            params = { 'page' : page_index+1 }
            params.update(self.setting('standard-params'))

            result = requests.get(
                    self.setting('base-url'),
                    params = params)

            filepath = os.path.join(self.work_dir(), "data-%s.html" % page_index)
            with codecs.open(filepath, 'wb', encoding="utf-8") as f:
                f.write(result.text)

    def parse(self):
        for filename in os.listdir(self.cache_dir()):
            filepath = os.path.join(self.cache_dir(), filename)
            print "found", filepath

            with codecs.open(filepath, 'rb', encoding="utf-8") as f:
                soup = BeautifulSoup(f)

                for i in range(1,100):
                    print "processing journal", i
                    journal = Journal()
                    select = "#record%s" % i

                    records = soup.select(select)
                    if not records:
                        break

                    record = soup.select(select)[0]

                    data = record.find("div", class_="data")

                    link = data.find("a")
                    journal.title = link.find("b").text.strip()
                    journal.url = link['href'].replace(u"/doaj?func=further&amp;passme=", u"")

                    issn_label = data.find("strong")
                    assert issn_label.text == "ISSN/EISSN"
                    issn_data = issn_label.next_sibling.strip().split(" ")
                    assert issn_data[0] == u':'
                    journal.issn = issn_data[1]
                    if len(issn_data) == 3:
                        journal.eissn = issn_data[2]

                    if len(data.find_all("strong")) > 1:
                        subject_label = data.find_all("strong")[1]
                        assert subject_label.text == "Subject"
                        subject_link = subject_label.next_sibling.next_sibling
                        assert "func=subject" in subject_link['href']
                        journal.subject = subject_link.text.strip()

                    for item in data.find_all('b'):
                        value = None
                        if item and item.next_sibling:
                            if isinstance(item.next_sibling, basestring):
                                value = item.next_sibling.replace(":", "").strip()

                        if item.text == 'Country':
                            journal.country = value
                        elif item.text == 'Language':
                            journal.language = value
                        elif item.text == 'Start year':
                            if value:
                                journal.start_year = int(value)
                        elif item.text == 'License':
                            journal.license = item.next_sibling.next_sibling['href']
                        else:
                            pass

                    journal.save()