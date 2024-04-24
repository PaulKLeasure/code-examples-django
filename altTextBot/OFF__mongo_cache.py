from .cache_functions import buildTextBotTemplateCache, templateAssetsQuery
import pymongo
from pymongo import MongoClient
import datetime
import pprint
import datetime
# https://pymongo.readthedocs.io/en/stable/
# https://pymongo.readthedocs.io/en/stable/tutorial.html#making-a-connection-with-mongoclient

def test():
    client = MongoClient('mongoService', 27017,
                          username='root',
                          password='rootpassword',
                          authSource='admin',
                          authMechanism='SCRAM-SHA-256')

    db = client.test_cache_database
    altTextData = db.altTextData
    altText = {
        "assetId": 123456789,
        "path": "/",
        "recursive": False,
        "requiredOptionIds": [123,456,678,345],
        "groupHeader": "General",
        "date": datetime.datetime.now(tz=datetime.timezone.utc),
    }

    altTextData.insert_one(altText).inserted_id
    pprint.pprint(altTextData.find_one())