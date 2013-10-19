from peewee import *
from oacensus.constants import dbfile

db = SqliteDatabase(dbfile)

class ModelBase(Model):
    class Meta:
        database = db
            
class Journal(ModelBase):
    title = CharField()
    url = CharField(null=True)

    issn = CharField(null=True)
    eissn = CharField(null=True)
    subject = CharField(null=True)
    country = CharField(null=True)
    language = CharField(null=True)
    license = CharField(null=True)
    start_year = IntegerField(null=True)

    iso_abbreviation = CharField(null=True)
    medline_ta = CharField(null=True)
    nlm_unique_id = CharField(null=True)
    issn_linking = CharField(null=True)

    def __unicode__(self):
        return u"<Journal {0}: {1}>".format(self.issn, self.title)

    def __str__(self):
        return unicode(self).encode('ascii', 'replace')

class Article(ModelBase):
    title = CharField()
    journal = ForeignKeyField(Journal, null=True)
    pubmed_id = CharField(null=True)
    nihm_id = CharField(null=True)
    pmc_id = CharField(null=True)
    date_published = DateField(null=True)
    date_created = DateField(null=True)
    date_completed = DateField(null=True)

    def __unicode__(self):
        return u'{0}'.format(self.title)

class Publisher(ModelBase):
    name = CharField()

class JournalList(ModelBase):
    name = CharField()

    def __str__(self):
        args = (len(self.journals()), self.name)
        return "<Journal List (%s journals): %s>" % args

    def add_journal(self, journal):
        JournalListMembership(
            journal_list = self,
            journal = journal).save()

    def journals(self):
        return [membership.journal for membership in self.memberships]

class JournalListMembership(ModelBase):
    journal_list = ForeignKeyField(JournalList, related_name="memberships")
    journal = ForeignKeyField(Journal, related_name="memberships")

class ArticleList(ModelBase):
    name = CharField()

Article.create_table()
Journal.create_table()
Publisher.create_table()
ArticleList.create_table()
JournalList.create_table()
JournalListMembership.create_table()