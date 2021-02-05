import json
import datetime

from peewee import *
from playhouse.sqlite_ext import *


# defines
db = SqliteExtDatabase('../var/settings.db')


# classes
class Setting(Model):
    key = CharField(unique=True)
    value = JSONField()
    modified = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db


# create database if necessary
with db:
    db.create_tables([Setting])

# import defaults if necessary
with open('./defaults.json', 'r') as fp:
    defaults = json.load(fp)
    for key in defaults:
        Setting.insert(key=key, value=defaults[key]).on_conflict('IGNORE').execute()
