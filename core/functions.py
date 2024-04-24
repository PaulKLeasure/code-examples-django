from core.models import Asset, Option, Category, ivault_t_search, ivault_t_options, ivault_t_vals
from core.serializers import AssetSerializer, OptionSerializer
from django.core.exceptions import ObjectDoesNotExist
import json
from django.http import HttpRequest, HttpResponse, JsonResponse
from pprint import pprint
from datetime import datetime
import pytz
import json
import os
import inspect
from iv_logger.functions import commitLogEntryToDatabase, build_log_text, ensureLog



"""
   For backwards compatability with wellborn.com Curator
"""
def create_core_ivault_t_options(searialOptDat=None):
    logMode = "backward_compatible"
    #print('create_core_ivault_t_options(): ') 
    #pprint(searialOptDat)
    if searialOptDat:
        """
           CREATE core_ivault_t_search
        """
        try:
            ivaultTOption = ivault_t_options(id=int(searialOptDat['id']), groupName=searialOptDat['grp'], definition=searialOptDat['def1'], groupSort=searialOptDat['grp_srt'])
            ivaultTOption.save()
            commitLogEntryToDatabase(":bkwd cmpatbl create", "bkwd cmpatbl CREATE OPTION", "ivault_t_options", ivaultTOption, logMode)      
        except ObjectDoesNotExist:
            err_text = "ERROR: core.functions.update_core_ivault_t_search_and_vals() Failed to find "+searialOptDat['def1']+"::"+searialOptDat['def1']+" in core_ivault_t_options"
            commitLogEntryToDatabase(":bkwd cmpatbl create", "bkwd cmpatbl CREATE", "ivault_t_options", {}, logMode, err_text)
            print(err_text)

"""
   For backwards UPDATE compatability with wellborn.com Curator
"""
def update_core_ivault_t_options(searialOptDat=None):
    logMode = "backward_compatible"
    #print('update_core_ivault_t_options(): ') 
    #pprint(searialOptDat)
    if searialOptDat:
        """
           UPDATE core_ivault_t_search
        """
        try:
            ivaultTOption = ivault_t_search.objects.get(id=int(searialOptDat['id']))
            ivaultTOption.groupName = searialOptDat['grp']
            ivaultTOption.definition = searialOptDat['def1']
            ivaultTOption.groupSort = searialOptDat['grp_srt']
            ivaultTOption.save()
            commitLogEntryToDatabase(":bkwd cmpatbl updt", "bkwd cmpatbl UPDATE", "ivault_t_search", ivaultTOption, logMode)      
        except ObjectDoesNotExist:
            err_text = "ERROR: core.functions.update_core_ivault_t_options() Failed to find "+f_name+" in core_ivault_t_search/vals"
            commitLogEntryToDatabase(":bkwd cmpatbl updt", "bkwd cmpatbl UPDATE", "ivault_t_search", {}, logMode, err_text)
            print(err_text)

"""
   For backwards DELETE compatability with wellborn.com Curator
"""
def delete_core_ivault_t_options(searialOptDat=None):
    logMode = "backward_compatible"
    #print('delete_core_ivault_t_options(): ') 
    #pprint(searialOptDat)
    if searialOptDat:
        ivaultTOptionObj = ivault_t_search.objects.get(id=int(searialOptDat.id))
        ivaultTOptionObj.delete()
        commitLogEntryToDatabase(":bkwd cmpatbl updt", "delete", "ivault_t_option", ivaultTOptionObj, logMode)

        """
           DELETE from core_ivault_t_vals
        """ 
        ivaultTValsObjects = ivault_t_vals.objects.filter(optId=int(searialOptDat.id))
        for ivTValobj in ivaultTValsObjects:
            ivTValobj.delete()
            commitLogEntryToDatabase(":bkwd cmpatbl delete", "delete", "ivault_t_vals", ivaultTOptionObj, logMode, "Option "+searialOptDat.groupName+"::"+searialOptDat.definition +" was deleted so this row was allso deleted")





"""
   For backwards compatability with wellborn.com Curator
"""
def create_core_ivault_t_search_and_vals(searialAssDat=None):

    #print('create_core_ivault_t_search_and_vals(): ') 
    #pprint(searialAssDat)
    logMode = "backward_compatible"
    if searialAssDat:
        f_name = searialAssDat['fileName'].replace("media", "").replace("/","")
        s_string = searialAssDat['search_string']
        optionIds = searialAssDat['search_string'].split("--")
        timestampIn = searialAssDat['timestamp']
        """
           CREATE core_ivault_t_search
        """
        try:
            ivaultTSearchObject = ivault_t_search(fileName=f_name)
            ivaultTSearchObject.search_string = s_string
            ivaultTSearchObject.save()
            commitLogEntryToDatabase(":bkwd cmpatbl create", "bkwd cmpatbl CREATE", "ivault_t_search", ivaultTSearchObject, logMode)      
        except ObjectDoesNotExist:
            err_text = "ERROR: core.functions.update_core_ivault_t_search_and_vals() Failed to find "+f_name+" in core_ivault_t_search/vals"
            commitLogEntryToDatabase(":bkwd cmpatbl create", "bkwd cmpatbl CREATE", "ivault_t_search", {}, logMode, err_text)
            print(err_text)

        """
           CREATE core_ivault_t_vals
        """
        for optId in optionIds:
            if optId.strip() != "":
                try:    
                    ivaultTValsObject = ivault_t_vals(fileName=f_name, optId=int(optId), selected="", option_group="", option_text="", resolution="")
                    ivaultTValsObject.save()
                    commitLogEntryToDatabase(":bkwd cmpatbl create", "bkwd cmpatbl CREATE", "ivault_t_vals", ivaultTValsObject, logMode )
                
                except ObjectDoesNotExist:
                    err_text = "ERROR: core.functions.update_core_ivault_t_search_and_vals() Failed to find "+f_name+":: option("+optId+") in core_ivault_t_vals"
                    commitLogEntryToDatabase(":bkwd cmpatbl create", "bkwd cmpatbl CREATE", "ivault_t_search/vals", ivaultTValsObject,logMode, err_text)
                    print(err_text)




"""
   For backwards UPDATE compatability with wellborn.com Curator
"""
def update_core_ivault_t_search_and_vals(searialAssDat=None):
    logMode = "backward_compatible"
    #print('update_core_ivault_t_search_and_vals(): ') 
    #pprint(searialAssDat)
    if searialAssDat:
        f_name = searialAssDat['fileName'].replace("media", "").replace("/","")
        s_string = str(searialAssDat['search_string'])
        timestampIn = searialAssDat['timestamp']
        optionIds = searialAssDat['search_string'].split("--")
        pseudoObject = {}
        pseudoObject['fileName'] = f_name   
        """
           UPDATE core_ivault_t_search
        """
        try:
            ivaultTSearchObject = ivault_t_search.objects.get(fileName=f_name.replace("%20", " "))
            ivaultTSearchObject.search_string = s_string
            ivaultTSearchObject.timestamp = timestampIn            
            ivaultTSearchObject.save()
            commitLogEntryToDatabase(":bkwd cmpatbl updt", "bkwd cmpatbl UPDATE", "ivault_t_search", ivaultTSearchObject, logMode)      
        except Exception as err:
            err_text = "LEGACY DATA ERROR: core.functions.update_core_ivault_t_search_and_vals() Failed to find "+f_name+" in core_ivault_t_search/vals"
            err_text = err_text + " Python Error: " + str(err)
            print('======== ERROR in update_core_ivault_t_search_and_vals() ======================')
            print(err_text)
            commitLogEntryToDatabase(":bkwd cmpatbl updt", "bkwd cmpatbl UPDATE", "ivault_t_search",  pseudoObject, logMode, err_text)

        """
           UPDATE core_ivault_t_vals
        """
        # Remove the ivault_t_vals prior to add back in the updated options
        ivaultTValsObjs = ivault_t_vals.objects.filter(fileName=f_name)
        for tValsObj in ivaultTValsObjs:
            tValsObj.delete()
            #commitLogEntryToDatabase(":bkwd cmpatbl updt", "bkwd cmpatbl DELETE", "ivault_t_vals", tValsObj, logMode)

        for optId in optionIds:
            if optId.strip() != "":
                try:    
                    ivaultTValsObject = ivault_t_vals(fileName=f_name, optId=int(optId), selected="", option_group="", option_text="", resolution="")
                    ivaultTValsObject.save()
                    commitLogEntryToDatabase(":bkwd cmpatbl updt", "bkwd cmpatbl UPDATE", "ivault_t_vals", ivaultTValsObject, logMode)
                except:
                    err_text = "LEGACY DATA ERROR: core.functions.update_core_ivault_t_search_and_vals() Failed to find "+f_name+":: option("+optId+") in core_ivault_t_vals"
                    commitLogEntryToDatabase(":bkwd cmpatbl updt", "bkwd cmpatbl UPDATE", "ivault_t_search", ivaultTValsObject, logMode, err_text)
                    print(err_text)


"""
   For backwards DELETE compatability with wellborn.com Curator
"""
def delete_core_ivault_t_search_and_vals(searialAssDat=None):
    ivaultTSearchObject = False
    ivaultTValsObjs = False
    logMode = "backward_compatible"
    #print('delete_core_ivault_t_search_and_vals(): ') 
    #pprint(searialAssDat)

    if searialAssDat:
        f_name = searialAssDat['fileName'].replace("media", "").replace("/","")
        pseudoObject = {}
        pseudoObject['fileName'] = f_name   
        try:
            print('---------------- TRY SEARCH '+f_name+'------------------')
            ivaultTSearchObject = ivault_t_search.objects.get(fileName=f_name)
            ivaultTSearchObject.delete()
            commitLogEntryToDatabase(":bkwd cmpatbl updt", "delete", "ivault_t_search", ivaultTSearchObject, logMode)
            print('---------------- TRY SEARCH DONE ------------------')
        except:
            pass
        finally:
            if(not ivaultTSearchObject):
               print('---------------- FINALLY SEARCH '+f_name+'------------------')
               err_text = "LEGACY DATA ERROR: core.functions.update_core_ivault_t_search_and_vals() Failed to find "+f_name+" in core_ivault_t_search"
               commitLogEntryToDatabase(":bkwd cmpatbl updt", "bkwd cmpatbl UPDATE", "ivault_t_search",  pseudoObject, logMode, err_text) 
               print('---------------- FINALLY SEARCH DONE------------------')
        
        """
           DELETE core_ivault_t_vals
        """
        # Remove the ivault_t_vals
        try:
            print('---------------- TRY VALS ------------------')
            ivaultTValsObjs = ivault_t_vals.objects.filter(fileName=f_name)
            for tValsObj in ivaultTValsObjs:
                tValsObj.delete()
                commitLogEntryToDatabase(":bkwd cmpatbl updt", "delete", "ivault_t_vals", tValsObj, logMode)
                print('---------------- TRY VALS DONE '+str(tValsObj.optId)+' ------------------')
        except:
            pass
        finally:
            if(not ivaultTValsObjs):
               print('---------------- FINALLY VALS -------------------')
               err_text = "LEGACY DATA ERROR: core.functions.update_core_ivault_t_search_and_vals() Failed to find "+f_name+" in core_ivault_t_vals"
               commitLogEntryToDatabase(":bkwd cmpatbl updt", "bkwd cmpatbl UPDATE", "ivault_t_vals",  pseudoObject, logMode, err_text) 
               print('---------------- FINALLY VALS DONE------------------')           

         


        





"""
SELF HEALING OPTIONS tag assignment relations for legacy Assets or corrupted Assets
AssObj.search_string  should be identical to whats in the core_asset_options table.
Based on Team decision made 2022-01-12, 
If Asset.search_string tags do not match the core_asset_options table,
This "Self healing" function will asses the IDs of both sources, combine them,
and then dedupify the list. Then the Asset will be updated with those option IDs.
This has been designed to be idempotent.
"""
def selfHealAssetOptions(assetObj):
    #print("SELF HEALING: core.functions.selfHealAssetOptions() ")
    date = datetime.now(pytz.timezone('US/Central'))
    timestampString = date.strftime("%Y-%m-%d %H:%M:%S")
    assetObj.timestamp = datetime.now(pytz.timezone('US/Central'))
    searchStringIds = createListOfOptionsIdsFromAssetSearchString(assetObj)
    alreadyRelatedOptIds = createListOfOptionsIdsFromAssetOptions(assetObj)
    searchStringIds.sort()
    alreadyRelatedOptIds.sort()
    #pprint(assetOption_stringifier(alreadyRelatedOptIds))
    #pprint(assetOption_stringifier(alreadyRelatedOptIds))
    
    # If these are the same do nothing
    if alreadyRelatedOptIds == searchStringIds:
        pass
    else:
        # Combine and Dedupify into new final list of options
        combinedOptionsList = alreadyRelatedOptIds + searchStringIds
        dedupifiedOptionsList = []
        for coid in combinedOptionsList:
            if coid not in dedupifiedOptionsList:
                dedupifiedOptionsList.append(coid)
        
        # if orig search_string is not equal to origin options
        updateAssetOptionsAndAssetSearchString(assetObj, dedupifiedOptionsList)


def createListOfOptionsIdsFromAssetOptions(assetObj):
        alreadyRelatedOptIds = []
        serialAsset = AssetSerializer(assetObj, many=False)
        fromCoreAssetOptionsTable = serialAsset.data['options']
        # Make list of opt ids from the core_asset_options table
        for relatedOpt in fromCoreAssetOptionsTable:
            #print('==== INDIVIDUAL relatedOpt ====')
            #pprint(relatedOpt)
            listOfOptionTuples = relatedOpt.items()
            #pprint(listOfOptionTuples)
            for optTuple in listOfOptionTuples:
                if optTuple[0] == 'id':
                    optId = optTuple[1] 
                    #print("SELF HEALING: OptID("+str(optId) +") already in the core_asset_options table.")
                    alreadyRelatedOptIds.append(optId)
        return alreadyRelatedOptIds

def updateAssetOptionsAndAssetSearchString(assetObj, optionsList):
    finalOptions = Option.objects.filter(pk__in=optionsList)
    logMode = "self-healing"
    # reset (disassociate) options before adding the updated options set
    assetObj.options.clear()
    assetObj.search_string = ''

    for optObj in finalOptions:
        assetObj.options.add(optObj)

    assetObj.search_string = assetOption_stringifier(optionsList)
    assetObj.save()
   
    commitLogEntryToDatabase("API:self-healing-options", "self-healing", "Asset",  assetObj, logMode)

def createListOfOptionsIdsFromAssetSearchString(assetObj):
        searchStringIds = []
        serialAsset = AssetSerializer(assetObj, many=False)
        search_string = serialAsset.data['search_string']
        searchStringItems = search_string.split("--")
        for item in searchStringItems:
            if item.isdigit() :
                searchStringIds.append(int(item))
        return searchStringIds

def add_optIds_to_search_string(assObj):
    optionTags = []
    s_string = assObj.search_string



def assetOption_stringifier(optionsIdListIn):
    # Testing feedback print this function and the parent who called it.
    # print("Function " + inspect.stack()[0][3] + " was called by " + inspect.stack()[1][3] + " in " + REL_PATH ) 

    # Deduplicate
    optionsIdListDeduped = []
    for i in optionsIdListIn:
        if i not in optionsIdListDeduped:
            optionsIdListDeduped.append(i)

    s_string = "--"
    for oid in optionsIdListDeduped:
        s_string += str(oid) + "--"
    
    return s_string
    



