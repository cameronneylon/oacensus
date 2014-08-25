__author__ = 'cneylon'
from oacensus.commands import defaults
from oacensus.models import Article
from oacensus.scraper import Scraper
from oacensus.models import Repository
from oacensus.models import Journal
from tests.utils import setup_db
setup_db()


test_title_open = "Covalent Attachment of Proteins to Solid Supports and Surfaces via Sortase-Mediated Ligation"
test_title_incorrect = "A non-existent journal article title"
test_doi_open = '10.1371/journal.pone.0001164'
test_doi_embargoed = '10.1007/s00024-004-0394-3'
test_doi_closed = '10.1063/1.3663569'
test_doi_restricted = '10.1111/j.1365-2125.2009.03481.x'

xml_testfile_path = 'tests/core_test.xml'

# This is a DOI from the Crossref Labs 'Journal of Pyschoceramics' which should never appear in OpenAIRE
test_doi_no_response = '10.5555/12345678'

test_journal = Journal.create(title='test-journal',
                              source='test-core',
                              log='test-core')
article_titles = [test_title_open, test_title_incorrect]
for title in article_titles:
    Article.create(title=title,
                   source='test-core',
                   log='test-core',
                   period='test',
                   journal=test_journal)

scraper = Scraper.create_instance("core")

def test_core_process_method():
    import xml.etree.ElementTree as ET
    s = ''
    with open(xml_testfile_path, 'ru') as f:
        s = f.readlines()
    test_response = ET.fromstringlist(s)

    repo, url, ftr = scraper.core_process(test_response, test_title_open)

    assert type(repo) == Repository
    assert url == 'http://core.kmi.open.ac.uk/download/pdf/102962'
    assert ftr == True


def test_core_scraper():

    # Test cases #
    ##############
    # Does the scraper run properly?
    # Are the relevant repositories created?
    # Are titles that should be returned?
    # Are titles that shouldn't be returned not?

    # Scraper runs successfully
    scraper.run()

    # Repositories created properly
    r1 = Repository.select()
    repos = [r for r in r1]
    assert len(repos) > 0

    names = [r.name for r in r1]
    assert 'core' in names

    # All appropriate titles found and returned
    a = Article.select().where(Article.title == test_title_open)[0]
    assert a.instances is not None
    assert a.instance_for('core') is not None

    # Nonexistent doi not returned
    a = Article.select().where(Article.title == test_title_incorrect)[0]
    instances = [inst for inst in a.instances]
    assert len(instances) == 0

    # Test correct answer for 'open' case
    a = Article.select().where(Article.title == test_title_open)[0]
    assert a.is_free_to_read()

    # Test correct answer for non-responding cases
    a = Article.select().where(Article.title == test_title_incorrect)[0]
    assert a.is_free_to_read() == False




