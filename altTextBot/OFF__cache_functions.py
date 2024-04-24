from .models import AltTextTemplate, AltTextCache
from django.db import connection
from .serializers import AltTextTemplateSerializer, AltTextCacheSerializer
from .functions import processTemplateData, recallAltTextFromCache, deleteMemorizedAltText, memorizeAltText
from core.models import Asset
from core.views_api_option_crud import fetch_options_by_groupnames_string
from core.serializers import AssetSerializer
from django.db.models import Q # filter using operators '&' or '|'
import json
from django.http import HttpRequest, HttpResponse, JsonResponse
from pprint import pprint
import json

""" 
RECOMMENDATIONS:
 - Run this in its own util instance so that it can refresh cache often 
   without casuing latency on the primary iVault Service API
 - Might want to create reporting service to help keep track of what has
   been cached
"""

"""
  This function applys the templates in the altTextBot_alttexttemplate table
to build (or update) the altTextBot_alttextcache table.

Defaults:
  - skips items that are already cached    
  - Builds cache for all existing templates

params:
  specificTemplate (int) Used to specify a template instead of the default of ALL templates
  overrideAltTextCache (boole) if true, existing cache will be overwritten

"""
def buildTextBotTemplateCache(specificTemplate = False, overrideAltTextCache = False): 
    if isinstance(specificTemplate, int) and  specificTemplate > 0:
        templateObjs = getTextBotTemplates(specificTemplate)
    else:
        templateObjs = getTextBotTemplates()
    serializedTemplates = preprocessTemplates(templateObjs)
    for serializedTemplate in serializedTemplates:
        templateAssetsQuery(serializedTemplate, overrideAltTextCache)
    return {"serializedTemplates" : serializedTemplates, "state": "process started"}



def fetchAssetIdsByItsOptIds(optionIdList = [], format=None):
    ssetObjects =[]
    andedContains = Q()
    andedExclusions = Q()
    for optId in optionIdList:
        if optId < 0:
            #remove the minus sign
            optId = optId * -1
            nextId = "-" + str(optId) + "-"
            #add to the search_string__contains= (for exclusion)
            andedExclusions &= Q(search_string__contains=nextId) 
        else:
            nextId = "-" + str(optId) + "-"
            andedContains &= Q(search_string__contains=nextId) 
    assetObjects = Asset.objects.filter(andedContains).exclude(andedExclusions).values_list('id', flat=True).distinct()
    #query = Asset.objects.filter(andedContains).exclude(andedExclusions).values_list('id', flat=True).distinct().query
    return assetObjects


"""
This method gets all or 1 textBot template(s)
and returns a list (even if of only one template)
"""
def getTextBotTemplates(idIn=None): 
    if idIn is not None:
        return AltTextTemplate.objects.filter(id=idIn)
    else:
        return AltTextTemplate.objects.all()

"""
This method serializes the fetched templates
"""
def preprocessTemplates(templateObjects):
    serializedTemplates = []
    for tempObj in templateObjects:
        serializedTemplate = AltTextTemplateSerializer(tempObj, many=False)
        serializedTemplates.append(serializedTemplate.data)
    return serializedTemplates


"""
Fetch appropriate assets for the template(s)
use template data 

# Build this query for each template
# Iterate templates, iterate each id in grpHeader (if any) and query for msut have reqd ids
SELECT id, f_name, s_string
FROM core_asset
WHERE s_string LIKE "%-1274-%" <-- assuming it needs to be public
AND s_string LIKE "%-1021-%" <--|
AND s_string LIKE "%-1085-%"     }<----- From template.required_ids
AND s_string LIKE "%-3057-%"    |
AND s_string LIKE "%-1275-%" <--| 
AND s_string LIKE "%-93-%"   <---------- From iterating through the IDs within a specified template.grpHeader

# Then fetch alt text for each result and record in cache.

"""
def templateAssetsQuery(sTemplateData, overrideAltTextCache=False):
    aggregateReqdIdsAndItertionOfSpecifiedGroupId = []
    requiredIds = []
    optionsInGroup = []
    if sTemplateData and sTemplateData['requiredIds']:
        requiredIds = json.loads(json.dumps(sTemplateData['requiredIds']))
    if sTemplateData and isinstance(sTemplateData['grpHeader'], str):
        optionsInGroup = fetch_options_by_groupnames_string(sTemplateData['grpHeader'], ",", False)
    # load the req'd IDs into aggregateReqdIdsAndItertionOfSpecifiedGroupId
    for reqId in requiredIds:
        aggregateReqdIdsAndItertionOfSpecifiedGroupId.append(reqId)
    # iterate ids in a specified groupName
    if isinstance(optionsInGroup["ids"], (list, tuple)):
        for optionId in optionsInGroup["ids"]:
            # Load the Group Header ID into aggregateReqdIdsAndItertionOfSpecifiedGroupId one at a time and 
            # iterate the option in the group to the other required option IDs
            aggregateReqdIdsAndItertionOfSpecifiedGroupId.append(optionId)
            # fetch assets by combined required_ids & a single option specific to this iteration
            QuerySetAssetIds = fetchAssetIdsByItsOptIds(aggregateReqdIdsAndItertionOfSpecifiedGroupId)   
            # Remove this ID befor next iteration
            aggregateReqdIdsAndItertionOfSpecifiedGroupId.remove(optionId)
            for assetId in QuerySetAssetIds:                
                assetObjectResults = Asset.objects.filter(id=int(assetId))
                assetObject = assetObjectResults[0]
                serializedAsset = AssetSerializer(assetObject, many=False)
                AssetData = serializedAsset.data
                
                if overrideAltTextCache:
                    deleteMemorizedAltText(AssetData["id"], sTemplateData["path"])
                    altTextResults = False
                else:
                    # cache the result
                    altTextResults = recallAltTextFromCache(AssetData["id"], sTemplateData["path"])
                if not altTextResults:
                    # apply template to the asset ID using the template path
                    altTextResults = processTemplateData(AssetData, sTemplateData)
                    # Cache it
                    if altTextResults:
                        print("altTextResults")
                        pprint(altTextResults)
                        altTextData = []
                        if altTextResults['tokenMissingFromTemplate']:
                            altTextResults['altText']=False
                            altTextResults['sucess']=False
                            errMsg = 'Cached altText as False! At least one token needed for template is missing'
                            altTextResults['reason']=errMsg
                            pprint(altTextResults)
                            print(errMsg)
                            #errorMsg = 'Result not cached! Template contains at least one unfound token.'
                            #return { "sucess": False, "error": errorMsg}
                        # reformat altTextResults into a list, altTextData
                        # in order to work with the memorizeAltText() function
                        altTextData.append(altTextResults)
                        # insert into cache table
                        memorizeAltText(altTextData)
                        print(" ---->  CACHED IT  -->")
                else:
                    print(" ----> ALREADY IN CACHE  -->")




