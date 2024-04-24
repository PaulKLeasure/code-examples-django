˜from altTextBot.models import AltTextTemplate, AltTextCache
from altTextBot.serializers import AltTextTemplateSerializer, AltTextCacheSerializer
from altTextBot.functions_altText_mongo_crud import mongoRecallAltText
from core.models import Asset, Option
import core.functions as coreFuncs
from core.serializers import AssetSerializer, OptionSerializer
from django.core.exceptions import ObjectDoesNotExist
from core.settings import BASE_DIR
from django.db.models import Value, CharField, F
from django.http import HttpRequest, HttpResponse, JsonResponse
from pprint import pprint
from datetime import date, datetime
import pytz
import json
import os
from operator import itemgetter
# Using regex
import re
import inspect
from iv_logger.functions import commitLogEntryToDatabase, build_log_text, ensureLog

# Setup Relative path for feedback
os.chdir(os.path.dirname(__file__))
REL_PATH = __file__.replace(BASE_DIR, '')

def getAllAltTextTemplates():
    templates = []
    AltTextTemplateObjs = AltTextTemplate.objects.all()
    for AltTextTemplateObj in AltTextTemplateObjs:
        serializedTemplate = AltTextTemplateSerializer(AltTextTemplateObj, many=False)
        print("FUNCTION:: serializedTemplate: ")
        pprint(serializedTemplate.data)
        templates.append(serializedTemplate)
    return templates

def getSerialAssetDataById(aid):
    if(aid):
        try:
            AssetData = Asset.objects.get(id=aid)
            if(AssetData):
                serializedAsset = AssetSerializer(AssetData, many=False)
                return serializedAsset.data
        except ObjectDoesNotExist:
            context["error"] = "Asset " + str(aid) + " NOT found"
            context["success"] = " False "       
            context["message"] = "Error: " + str(aid) + " cannot be deleted becasue it does not exist in database!" 
            return JsonResponse(context, safe=False)
    else:
        print("Error: id parameter missing! in altTextBot:functions::getSerialAssetDataById(aid)")
        return False

def getSerialAssetDataByFilename(filename):
    context = {}
    if(filename):
        try:
            AssetData = Asset.objects.get(fileName=filename)
            if(AssetData):
                serializedAsset = AssetSerializer(AssetData, many=False)
                return serializedAsset.data
        except ObjectDoesNotExist:
            context["error"] = "Asset " + filename + " NOT found"
            context["success"] = " False "       
            context["message"] = "Error: " + filename + " cannot be deleted becasue it does not exist in database!" 
            return context
    else:
        print("Error: id parameter missing! in altTextBot:functions::getSerialAssetDataById(filename)")
        return False


"""

Default mode:
    The default mode is to return altextOnly if alt text exists in cache or null

GET Params:
    asCachedElseBlank Boole (default is True) indicates to return alt text if it exists in cache or else return nothing
    altTextOnly Boole (default is True) indicates to return only the alt text (if any)
    overrideCache Boole (default is False) Perform a fresh templated search and ovverride existing (or non-existing) cached results.
    showAltTextData Boole (default is False) Include alt text metadata
"""
def fetchAltText(serialAssetDataId, requestIn, isRecursive=True, pathIn=False):
    lineReturn = "\n"
    devFeedback = "DEV FEEDBACK: "+lineReturn
    # accommodates 2 ways to set the path
    if pathIn is not False:
        thisPath = pathIn
        devFeedback += "thispath from func(param) = " + str(thisPath) +lineReturn
    elif 'path' in requestIn.GET:
        thisPath = requestIn.GET.get('path')
        devFeedback += "thispath from GET = " + str(thisPath) +lineReturn
    else:
        # no path, no alt text
        return "Warning: No web uri path was supplied to obtain appropriate alt text with."
    results = "Alt text results not found."
    config = {}
    altTextData = False
    getParams = ["overrideCache", "showAltTextData", "asCachedElseBlank", "altTextOnly"]
    config["path"] = pathIn
    config["isRecursive"] = isRecursive
    config["overrideCache"] = False
    config["showAltTextData"] = False
    config["asCachedElseBlank"] = True
    config["altTextOnly"] = True
    
    print("========DEV FEEDBACK===============")
    print('fetchAltText:: PARAMS requestIn.GET')
    pprint(requestIn.GET)
    print("=======================")

    # Adjust params to the GET request params or leave default vals
    for param in getParams:
        if param in requestIn.GET:
            devFeedback += "config["+param+"] was "+ str(config[param]) +lineReturn
            if requestIn.GET.get(param).lower() == "true" or requestIn.GET.get(param).lower() == "false":
                config[param] = False if requestIn.GET.get(param).lower() == "false" else True
                devFeedback += "  --> config["+param+"] changed to "+ str(config[param])+" by GET param." +lineReturn
    
    if config["showAltTextData"]:
        config["altTextOnly"] = False
        devFeedback += "  --> config[altTextOnly] changed to False by TRUE config[showAltTextData] GET param." +lineReturn
    
    if config["overrideCache"]:
        config["asCachedElseBlank"] = False
        devFeedback += "  --> config[asCachedElseBlank] changed to False by TRUE config[overrideCache] GET param." +lineReturn

    """
    This will get a fresh calculation of the alt text
    ONLY if overrideCache  is True
    """
    #if not altTextData or overrideCache:
    if config["overrideCache"]:
        serialAssetData = getSerialAssetDataById(serialAssetDataId)
        altTextData = fetchAltTextTemplateResults(serialAssetData, requestIn, config["isRecursive"], pathIn)
        devFeedback += "overriden altTextData: " +lineReturn
    else:
        # This will get the mongo cached version of the alt text
        altTextData = mongoRecallAltText(int(serialAssetDataId), thisPath)
        #altTextData = recallAltTextFromCache(serialAssetDataId, thisPath)
        devFeedback += "existing altTextData: "  +lineReturn

    """
    This is invoked when the 'asCachedElseBlank' parameter is True and 
    will return False unless there is a cached version (without
    attempting to create cache) and also paying attention to the alt
    text only parameter.
    """
    #if config["asCachedElseBlank"]:
    if altTextData:
        if config["altTextOnly"]:
            results = altTextData["altText"]
        elif config["showAltTextData"]:
            results = processMongoResults(altTextData, "json", True)
    else:
        if config["overrideCache"]:
            results = "Alt text template match not found for Asset: "+str(serialAssetDataId)+"."
        else:
            results = "Alt text results not found in cache for Asset: "+str(serialAssetDataId)+"."

    return results


""" 



"""
def fetchAltTextTemplateResults(serialAssetData, requestIn, isRecursive=True, pathIn = False, isTest=False):
    altTextResults = False
    thisPath = False
    altTextResults = []
    if 'overrideCache'in requestIn.GET:
        overrideCache = True if requestIn.GET.get('overrideCache') == "True" else False
    else:
        overrideCache = False
        
    if pathIn:
        thisPath = pathIn
    elif 'path' in requestIn.GET:
        thisPath = requestIn.GET.get('path')

    # Path required. Dont bother if no path
    if not thisPath:
        return False
    
    """
    Assume recursive at first so any match may be found to work with.
    The following query uses the Django annotate method to 
    check and see if the AltTextTemplate::path field value
    is a sub-string of the input parameter thisPath.
    """
    FetchAltTextTemplates = AltTextTemplate.objects.annotate(
        string=Value(thisPath,output_field=CharField())
        ).filter(string__icontains=F('path')).all()
    if FetchAltTextTemplates:
        for AltTextTemplateObj in FetchAltTextTemplates:
            SerializedAltTextTemplate = AltTextTemplateSerializer(AltTextTemplateObj, many=False)
            data = SerializedAltTextTemplate.data
            print("======================")
            print(" TEMPLATE DATA: ")
            print("======================")
            pprint(data)           
            if data["isRecursive"] is not True :
                fetchedAltTextObj = getAltTextTemplateByExactPath(serialAssetData, data, thisPath)
            else:
                fetchedAltTextObj = getAltTextTemplateByRecursivePath(serialAssetData, data, thisPath)
            if fetchedAltTextObj:
                # print("##################")
                # pprint(fetchedAltTextObj)
                # print("##################")
                altTextResults.append(fetchedAltTextObj)
    # print('RESULTS (altTextResults):')
    # pprint(altTextResults)

    if overrideCache:
        deleteMemorizedAltText(serialAssetData["id"], thisPath)

    if altTextResults:
        if altTextResults[0]['tokenMissingFromTemplate']:
            altTextResults[0]['altText']=False
            altTextResults[0]['sucess']=False
            errMsg = 'Cached altText as False! At least one token needed for template is missing'
            altTextResults[0]['reason']=errMsg
            #pprint(altTextResults)
            #print(errMsg)
            #errorMsg = 'Result not cached! Template contains at least one unfound token.'
            #return { "sucess": False, "error": errorMsg}
        memorizeAltText(altTextResults)
    """ 
    The logic below is for the template testing results.
    """
    if isTest:
        altTextTestResults = []
        for altTextResult in altTextResults:
            if altTextResult["altText"]:
                resultObj = {}
                for item in altTextResult:
                    resultObj[item] = altTextResult[item]
                    if item == "tokenMissingFromTemplate":
                        tokensMissing = ", ".join(altTextResult['tokensMissing'])
                        numberOfTokensMissing = len(altTextResult['tokensMissing'])
                        pluralSuffix = ""
                        requiredBy = "a token"
                        if numberOfTokensMissing > 1 :
                            pluralSuffix = "s"
                            requiredBy = "the tokens"
                        if altTextResult[item] is not False:
                            resultObj['error'] = "If viewed from the path `"+ resultObj['path'] +"`, this asset has the required ids, but is missing at least "+str(numberOfTokensMissing)+" value"+pluralSuffix+" within" + ' the option group header'+pluralSuffix+', `' + str(tokensMissing) + '` required by the token'+pluralSuffix+' in this template. '+ ' This template will be prevented from showing the alt '+ 'text by AltTextBot:functions::templateInturprater(assetData, template)'
                        else:
                            resultObj['error'] = False
                    if resultObj not in altTextTestResults:
                        altTextTestResults.append(resultObj)
        return altTextTestResults
    else:
        return recallAltTextFromCache(serialAssetData["id"], thisPath)
    #return altTextResults

# Recall cache from sql
def recallAltTextFromCache(assetId, path):
    if(assetId):
        SerializedAltText = False
        AltTextCacheObjs = []
        AltTextCacheObjs = AltTextCache.objects.filter(assetId=assetId, path=path)
        if len(AltTextCacheObjs) >= 1:
            SerializedAltText = AltTextCacheSerializer(AltTextCacheObjs[0], many=False)
            data = SerializedAltText.data
            if data["altText"] == "False":
                data["altText"] = False
                data["message"] = "Alt Text cached as false. (no alt text)."
            data["sucess"] = True
            data["error"] = False
            return data
    return False

# Deletes cached result in SQL
def deleteMemorizedAltText(assetId, path):
    AltTextCacheObjs = []
    print("DELETING MemorizedAltText " + str(assetId) )
    AltTextCacheObjs = AltTextCache.objects.filter(assetId=assetId, path=path)
    if len(AltTextCacheObjs) >= 1:
        for obj in AltTextCacheObjs:
            obj.delete()
        print("DELETED MemorizedAltText " + str(assetId) )

# Caches the result in SQL
def memorizeAltText(altTextResults):
    print("Memorizing Alt Text ...")
    #pprint(altTextResults)
    altTextList = []
    prioritizeAltTextResults(altTextResults)
    # Sort altTextResults by sort order high number first
    altTextList = sorted(altTextResults, key=itemgetter('priority'), reverse=True) 
    # Create cache record from first in list (higher number)
    #print("-- SORTED altTextList --")
    #pprint(altTextList)
    if len(altTextList) > 0:
        altTextRecord = altTextList[0]
        if altTextRecord["altText"]:
            try:
                AltTextCacheObj = AltTextCache(assetId=int(altTextRecord["assetId"]), 
                templateId=int(altTextRecord["templateId"]))
                AltTextCacheObj.fileName=str(altTextRecord["assetFilename"])
                AltTextCacheObj.path=altTextRecord["path"] 
                AltTextCacheObj.altText=altTextRecord["altText"]
                AltTextCacheObj.save()
                print(" ----Template("+str(altTextRecord["templateId"])+") MEMORIZED to CACHE table! ----")
                return True
            except Exception as err:
                print("!-!-!-!-!-!-!-!-!-!-!-!-!-!")
                print("!-!-!-!-!-!-!-!-!-!-!-!-!-!")
                print("Error saving AltText Cache")
                print(err)
                print("filename: " + str(altTextRecord["assetFilename"]) )
                print( altTextRecord["assetFilename"].length )
                print("!-!-!-!-!-!-!-!-!-!-!-!-!-!")
                print("!-!-!-!-!-!-!-!-!-!-!-!-!-!")
                exit()
                return False
    else:
        print("No alt text results to remember!")
        return False

def prioritizeAltTextResults(altTextResults):
    dataDict = {}
    priority = 0
    prioritizedData = []

    if altTextResults[0]["altText"] is not False:
        print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
        print("prioritizeAltTextResults(altTextResults) =|0|=")
        print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
        pprint(altTextResults[0]["altText"])
    
    requiredGroupHeader = False
    requiredOptinIds    = False
    for i, data in enumerate(altTextResults):
        if data['grpHeader'] not in ["", " ", "none", "-", "false", "False","null","Null","NULL"]:
            priority += 1
        if len(data["requiredIds"]) >= 1:
            priority += 1
        if data["exact_path"]:
            priority += 1
        data["priority"] = priority
        data["sort"] = -priority
        prioritizedData.append(data) 
        priority = 0
    print(" =====>>  prioritizedData[priority]  ======")
    pprint(prioritizedData)
    return prioritizedData

"""
Replace tokens with appropiate values based on asset option IDs
"""
def templateInturprater(assetData, template):
    tokenMatches = []
    tokensMissing =[]
    data = {}
    # Extract substrings between brackets as tokens from template into a list using regex
    tokensFromTemplate = re.findall(r'\{{.*?\}}', template)
    numberOfTokens = len(tokensFromTemplate)
    #print("tokensFromTemplate LIST:")
    #pprint(tokensFromTemplate)
    tokenMissingFromTemplate = False
    for templateToken in tokensFromTemplate:
        print("templateToken = "+str(templateToken))
        tokenMatchData = {}
        tokenFetchData = fetchTokenValuesByAssetData(assetData, templateToken)
        if len(tokenFetchData["multiData"]) < 1: 
            tokenMissingFromTemplate = True
            tokensMissing.append(templateToken)
            print(" Teken MISSING from template")
        #print("++++   Token from Asset Data  ++++")
        #pprint(tokenFetchData)
        for tokenData in tokenFetchData["multiData"]:
            #print("tokenData -->-->-->")
            #print('tokenFetchData[multiData]')
            #pprint(tokenFetchData["multiData"])
            tokenVal = tokenData["definition"]
            #print("TOKEN VALUE:: "+ tokenVal)
            tokenMatchData[templateToken] = tokenVal
            tokenVal = grammeratizeCommaSeperatedString(tokenVal)
            tokenMatches.append(tokenMatchData)
            if tokenData['tokenFound'] is not True:
                # Unset template and break out of this loop
                template = 'Failed to inturprate: One or more tokens needed by template were not found'
                #foundAllTokens = False
                break
            if  tokenData['success'] is not True:
                # Unset template and break out of this loop
                template = 'Failed to inturprate: Token not sucessful'
                #foundAllTokens = False
                break
            # Insert token values into string
            if tokenVal is not None:
                # See if this token exists in the template
                # If it does replace it with the value
                template = template.replace(templateToken, tokenVal)
    #data['tokenVal'] = tokenVal   
    data['tokenMissingFromTemplate'] = tokenMissingFromTemplate
    data['tokensMissing'] = tokensMissing
    data['iturpratedText'] = template
    data['tokenMatches'] = tokenMatches
    if numberOfTokens == len(tokenMatches):
        data["allTokenValsFound"] = True
    else:
        data["allTokenValsFound"] = False
    #data['foundAllTokens'] = foundAllTokens
    #print(";;;;;;;;;;;;;")
    #print("TOKEN DATA:")
    #pprint(data)
    #print(";;;;;;;;;;;;;")
    return data

"""
Find which asset option id(s) have grp(s) matching the token(s)
and return the data
(Token is the same as an Option grp)
"""
def fetchTokenValuesByAssetData(assetData, token):
    context = {}
    context["error"] = ""
    data = {}
    tokenGroupsFound = []
    multiData = []
    sep = "~"
    assetOptionIds = getOptionIdsListFromAssetData(assetData)
    # Return the definition value for the matching ID
    for oid in assetOptionIds:
        # Fetch the option data
        # print("OPTION ID: "+str(oid))
        try:
            optionObj = Option.objects.get(id=oid)           
            serializedOption = OptionSerializer(optionObj, many=False)
            optionData = serializedOption.data
            optionData["success"] = False
            optionData["tokenFound"] = False
            tokenGroupName = token.replace("{{","").replace("}}","")                       
            if optionData["groupName"] == tokenGroupName:
                optionData["success"] = True
                optionData["tokenFound"] = True
                """
                If there are multiple defs with same grp, 
                concatinate them into a comma sep'd string list
                """
                if tokenGroupName in tokenGroupsFound:
                    for index, grpDat in enumerate(multiData):
                        if grpDat["groupName"] == tokenGroupName:
                            grpDat["definition"] += sep + optionData["definition"]
                    multiData[index]["definition"] = grpDat["definition"]
                else:
                    multiData.append(optionData)
                if tokenGroupName not in tokenGroupsFound:
                    tokenGroupsFound.append(tokenGroupName)    
                context["multiData"] = multiData            
            else:
                optionData["groupName"] = ''
                optionData["definition"] = ''
                optionData["tokenFound"] = False
                context["multiData"] = multiData
            
        except ObjectDoesNotExist:
            context["success"] = False
            context["error"] += ", Asset object NOT found in AltTextBot::fethTokenValueByAssetData(assetData, token) " + REL_PATH 
            context["tokenFound"] = False
            context["multiData"] = multiData
    
    return context

def grammeratizeBetweenVowelsAndCon(input, sep=","):
    # Turns out this is a big ask
    pass

def grammeratizeCommaSeperatedString(input, sep="~"):
    # make a list from this
    stringIn = str(input)
    listfromStr = stringIn.split(sep)
    if len(listfromStr) > 1:
        if len(listfromStr) == 2:
            # seperate with " and "
            rebuildStr = " and ".join(listfromStr)
            return rebuildStr
        else:
            # alter the last occurance with "and " and rejoin with ", "
            listfromStr[len(listfromStr) - 1] = "and "+ listfromStr[len(listfromStr) - 1]
            rebuildStr = ", ".join(listfromStr)
            return rebuildStr
    else:
        return input

def getAltTextTemplateByRecursivePath(serialAssetData, data, thisPath):
    pprint(data)
    print(data["path"])
    dataPath = data["path"]
    # Resursive path case
    if dataPath == thisPath or dataPath in thisPath :
        print("RECURSIVE PATH REQ'd and PASSED")
        resDat = processFilterConditions(serialAssetData, data, thisPath)
        #print("resDat::")
        #pprint(resDat)
        return resDat
    else:
        #print("RECURSIVE PATH REQ'd but FAILED")
        return False

def getAltTextTemplateByExactPath(serialAssetData, data, thisPath):
    # Exact match case
    if data["path"] == thisPath:
        #print("EXACT PATH REQ'd and  PASSED")
        resDat = processFilterConditions(serialAssetData, data, thisPath)
        return resDat
    else:
        #print("EXACT PATH REQ'd but FAILED")
        return False

def processFilterConditions(serialAssetData, data, thisPath):
    if filterAgainstRequiredIds(serialAssetData, data):
        if filterForInOptionGroup(serialAssetData, data):
            return processTemplateData(serialAssetData, data)
        else:
            return False
    else:
        return False

"""
If the requiredIds not indicated, then just return True because
this conditions is being ignored.
Else check to see if any of the Req'd Option IDs are in the Asset 
and return false if not.
"""
def filterAgainstRequiredIds(serialAssetData, data):
    print(" IN DEF filterAgainstRequiredIds() ")
    filterListSet = set(data['requiredIds'])
    # check if all elements in ls are integers
    if type(data['requiredIds']) is not "list":
        print("RequiredIds Conditon: NO REQUIRED IDs so ignored and remains TRUE")
        return True
    elif not all([isinstance(item, int) for item in data['requiredIds']]):
        print("RequiredIds Conditon: NO REQUIRED IDs so ignored and remains TRUE")
        return True
    else:
        assetOptionIds = getOptionIdsListFromAssetData(serialAssetData)
        assetOptIdSet = set(assetOptionIds)
        intersectionOfIds = list(filterListSet.intersection(assetOptIdSet))
        # Sort before comparing for equality
        intersectionOfIds.sort()
        data['requiredIds'].sort()
        if data['requiredIds'] == intersectionOfIds:
            print("RequiredIds Conditon: REQUIRED and TRUE")
            return True
        else:
            print("RequiredIds Conditon: REQUIRED but FALSE")
            return False

"""
If the grpHeader in not indicated, then just return True because
this conditions is being ignored.
Else check to see if any of the asset option IDs are in
the Option Group Header collection and return false if not.
"""
def filterForInOptionGroup(serialAssetData, data):
    print("  def filterForInOptionGroup(serialAssetData, data)  ")
    # Test here if template includes an "all in group header" condition
    if data['grpHeader'] in ["", " ", "none", "-", "false", "False","null","Null","NULL"]:
        print("GROUP HEADER Conditon: NOT REQUIRED but TRUE")
        return True
    else:
        idsInOptionGroup = getAllIdsInAnOptionGroup(data['grpHeader'])
        assetOptionIds = getOptionIdsListFromAssetData(serialAssetData)
        if assetOptionIds:
            for oid in idsInOptionGroup:
                if oid in assetOptionIds:
                    print("GROUP HEADER Conditon: REQUIRED and TRUE")
                    return True
        print("GROUP HEADER Conditon: REQUIRED and FALSE")
        return False

def processTemplateData(serialAssetData, data):
    #print("process Template Data:: DATA")
    #pprint(serialAssetData)
    dataDict = {}
    sort = 0
    templateData = templateInturprater(serialAssetData, data['template'])
    #print("LINE:379 templateData")
    #pprint(templateData)
    dataDict['templateId'] = data["id"]
    dataDict['path'] = data["path"]
    dataDict['assetId'] = serialAssetData['id']
    dataDict['assetFilename'] = str(serialAssetData["fileName"])
    dataDict['exact_path'] = not data["isRecursive"]
    dataDict['grpHeader'] = data["grpHeader"]
    dataDict['requiredIds'] = data["requiredIds"]
    dataDict['altText'] = templateData['iturpratedText']
    dataDict['tokenMissingFromTemplate'] = templateData['tokenMissingFromTemplate']
    dataDict['tokensMissing'] = templateData['tokensMissing']
    dataDict['altTextTemplate'] = data['template']
    dataDict['f_name'] = str(serialAssetData["fileName"])
    dataDict['sort'] = (sort + 1) if not data["isRecursive"] else sort
    return dataDict

def getAllIdsInAnOptionGroup(grp_name):
    ids = []
    optionObjs = Option.objects.filter(groupName=grp_name)
    for optObj in optionObjs:
        ids.append(optObj.id)
    return ids

def getOptionIdsListFromAssetData(serialAssetData):
    res = False
    # Make sure this is fully serialized data
    if serialAssetData and not isinstance(serialAssetData,dict):
        if(serialAssetData.data):
            serialAssetData = serialAssetData.Data
    
    if serialAssetData and 'search_string' in serialAssetData:
        assetOptionIds=[]
        searchStringItems = serialAssetData['search_string'].split("--")
        searchStringItems = searchStringItems
        for item in searchStringItems:
            if item.isdigit() :
                assetOptionIds.append(int(item))
        return assetOptionIds
    else:
        return res

def processMultiFromSameGroup(serialAssetData, grp_name):
    #print("  def processMultiFromSameGroup(serialAssetData, data)  ")
    ids = []
    idsInOptionGroup = getAllIdsInAnOptionGroup(grp_name)
    assetOptionIds = getOptionIdsListFromAssetData(serialAssetData)
    for oid in idsInOptionGroup:
        if oid in assetOptionIds:
            if oid not in ids:
                ids.append(oid)
    return ids






    """

Default mode:
    The default mode is to return altextOnly if alt text exists in cache or null

GET Params:
    asCachedElseBlank Boole (default is True) indicates to return alt text if it exists in cache or else return nothing
    altTextOnly Boole (default is True) indicates to return only the alt text (if any)
    overrideCache Boole (default is False) Perform a fresh templated search and ovverride existing (or non-existing) cached results.
    showAltTextData Boole (default is False) Include alt text metadata
"""
def fetchAltTextByTemplate(assetId, template):
    lineReturn = "\n"
    devFeedback = "DEV FEEDBACK: "+lineReturn
    results = "Alt text results not found."
    config = {}
    altTextData = False
    config["path"] = template["path"]
    config["isRecursive"] = template["recursive"]
    config["overrideCache"] = True
    config["showAltTextData"] = False
    config["asCachedElseBlank"] = False
    config["altTextOnly"] = True
    
    #print("========DEV FEEDBACK===============")
    #print('fetchAltText:: PARAMS requestIn.GET')
    #pprint(requestIn.GET)
    #print("=======================")

    """
    This will get a fresh calculation of the alt text
    """
    serialAssetData = getSerialAssetDataById(assetId)
    altTextData = fetchAltTextTemplateResults(serialAssetData, requestIn, config["isRecursive"], pathIn)
    devFeedback += "overriden altTextData: " +lineReturn

    """
    This is invoked when the 'asCachedElseBlank' parameter is True and 
    will return False unless there is a cached version (without
    attempting to create cache) and also paying attention to the alt
    text only parameter.
    """
    #if config["asCachedElseBlank"]:
    if altTextData:
        if config["altTextOnly"]:
            results = altTextData["altText"]
        elif config["showAltTextData"]:
            results = altTextData
    else:
        if config["overrideCache"]:
            results = "Alt text template match not found for Asset: "+str(serialAssetDataId)+"."
        else:
            results = "Alt text results not found in cache for Asset: "+str(serialAssetDataId)+"."
    
    #print("================ DEV FEEDBACK: ==============")
    ##devFeedback += "Results returned: "+ str(results) +lineReturn
    #print(devFeedback)
    #pprint(results)
    #print("=============================================")
    return results

def processMongoResults(mongoResult, outputType="json", echo=False):
    if isinstance( mongoResult, dict):
        if '_id' in mongoResult.keys():
            mongoResult['_id'] = str(mongoResult['_id'])
        if 'date' in mongoResult.keys(): 
            mongoResult['date'] = mongoResult['date'].isoformat()
        if outputType.lower() == "jsonstring":
            data = json.dumps(mongoResult)
        if outputType == "json":
            data = json.loads(json.dumps(mongoResult))
        if echo:
            print("====== def processMongoResults(mongoResult, outputType, echo=True) ===========")
            print ("Mongo result in ...")
            pprint(mongoResult)
            print("Mongo result converted:")
            pprint(data)
            print("====== ALT TEXT DATA ===========")
        return data