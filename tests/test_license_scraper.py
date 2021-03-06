from oacensus.scraper import Scraper
from oacensus.models import License
from oacensus.models import delete_all
from tests.utils import setup_db

setup_db(create_licenses=False)

def test_license_scraper_all_licenses():
    delete_all(delete_licenses=True)
    assert License.select().count() == 0
    scraper = Scraper.create_instance('licenses')
    scraper.run()
    assert License.select().count() == 6

    cc_by = License.find_license("cc-by")
    assert cc_by.title == "Creative Commons Attribution"
