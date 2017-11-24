from peewee import Model
from peewee_async import MySQLDatabase

database = MySQLDatabase(None)


class BaseModel(Model):

    """Base model for db"""
    class Meta:
        database = database
