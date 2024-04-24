from .models import AltTextTemplate, AltTextCache
import sys
import pymongo
import datetime
from django.db import connection
from altTextBot.serializers import AltTextTemplateSerializer, AltTextCacheSerializer
from core.models import Asset
from core.serializers import AssetSerializer
from pprint import pprint
import json
from dotenv import load_dotenv
load_dotenv()
import logging
import os
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))


""" 
CREATE
"""
def mongoSaveAltTextCache(altText):
    client = determineMongoDbClient()
    database = determineMongoDatabase(client)
    altTextDataCollection = determineMongoCollection(database)
    
    checkExistsArr = mongoRecallAltText(altText["assetId"], altText["path"])
    # print("////--->>> checkExistsArr")
    # pprint(checkExistsArr)

    if checkExistsArr is None or checkExistsArr is False:
        altText = {
            "assetId": altText["assetId"],
            "assetFilename": str(altText["f_name"]),
            "path": altText["path"],
            "altText": altText["altText"],
            "templateId": altText["templateId"],
            "date": datetime.datetime.now(tz=datetime.timezone.utc),
        }
        try:
            altCachedId = altTextDataCollection.insert_one(altText).inserted_id
            print("mongoSaveAltTextCache() INSERTED:()")
            #pprint(altCachedId)
            return altCachedId
        except pymongo.errors.OperationFailure:
            print("ERROR: mongoSaveAltTextCache(asset: "+str(altText["assetId"])+" INSERT FAILDED ")
            pprint(altText)
            return False
    else:
        print("ASSET EXISTED; "+str(altText["assetId"])+" Not inserted.")
        return False


""" 
READ 
"""
def mongoRecallAltText(assetId, path):
    client = determineMongoDbClient()
    database = determineMongoDatabase(client)
    altTextDataCollection = determineMongoCollection(database)
    if altTextDataCollection is not None:
        try:
            result = altTextDataCollection.find_one( { "assetId": assetId, "path": path } )
            client.close()
            return result
        except pymongo.errors.OperationFailure as e:
            print("ERROR:  pymongo.MongoClient(connStr) : ")
            print(e.code)
            print(e.details)            
            print("This collection doesn't exist")
            return False
    else:
        return False


""" 
UPDATE (for futuer)
https://www.geeksforgeeks.org/python-mongodb-update_one/
 - update based on mongo  _id
 - update based on assetId and path
 - update based on fileName and path
"""


""" 
DELETE 
"""
def mongoDeleteAltTextCache(assetId, path):
    client = determineMongoDbClient()
    database = determineMongoDatabase(client)
    altTextDataCollection = determineMongoCollection(database)
    print("mongoDeleteAltTextCache(assetId, path):")
    pprint(altTextDataCollection)
    if altTextDataCollection is not None:
        altTextDataCollection.deleteOne( { "assetId": assetId, "path": path } )
        client.close()
    else:
        return False

"""
Build connection string based on environment

"""
def determineMongoDbClient():
    env = str(os.environ['ENVIRONMENT'])
    # Docker environment if localDev
    if "localdev" == env.lower():
        print("=== LOCAL DEV ENVIRONMENT ==== def determineMongoDbClient()")
        cli =  pymongo.MongoClient('mongoService', 27017, username='root', password='rootpassword', authSource='admin', authMechanism='SCRAM-SHA-256') 
        print("def determineMongoDbClient() cli = ")
        #pprint(cli)
        return cli
    # AWS DocumentDB for live environments  env = str(os.environ['ENVIRONMENT'])
    if "prod" in env.lower() or "stage" in env.lower() or "dev" in env.lower():
        mongoHost = os.environ['mongoHost']
        mongoUsername = os.environ['mongoUsername']
        mongoPasscode = os.environ['mongoPasscode']
        mongoPemKeyPath = os.environ['mongoPemKeyPath']
        connStr = 'mongodb://'+ mongoUsername +':'+ mongoPasscode +'@'+ mongoHost +':27017/'
        connStr += '?tls=true&tlsCAFile=' + mongoPemKeyPath
        connStr += '&replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false'
        try:
            cli = pymongo.MongoClient(connStr)
        except pymongo.errors.OperationFailure as e:
            print("ERROR:  pymongo.MongoClient(connStr) : ")
            print(e.code)
            print(e.details)
            return False
        pprint(cli)
        return cli
    
    sys.exit('NOT a RECOGNIZED ENVIRONMENT!' + env)

def determineMongoDatabase(client):
    env = str(os.environ['ENVIRONMENT'])
    #client = determineMongoDbClient()
    print("client = def determineMongoDatabase()")
    pprint(client)
    #return client.localdev_textBot
    if "localdev" in env.lower():
        return client.localdev_textBot
    if "dev" in env.lower():
        return client.dev_textBot
    if "stage" in env.lower():
        return client.stage_textBot
    if "prod" in env.lower():
        return client.prod_textBot

    sys.exit('NOT a RECOGNIZED ENVIRONMENT!' + env)

def determineMongoCollection(db):
    #db = determineMongoDatabase()
    ##Specify the database to be used
    return db.altText_cache



