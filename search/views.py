from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, redirect
from core.models import Asset, Option, Category
from core.serializers import AssetSerializer, OptionSerializer
from django.db.models import Q # filter using operators '&' or '|'
from django.db.models import Count
from pprint import pprint
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
import json



# Create your views here.
def SearchAssets(request):
    context = {}
    RESULTS_PER_PAGE = 12
    context['S3_iVault_uri'] = settings.S3_IVAULT_URI
    searchResults = ''
    queryString = optIds = request.GET.get('q')
    quanPerPage = 10
    if(request.GET.get('limit')):
        quanPerPage = request.GET.get('limit')
    
    #excludes = request.GET.get('excl')
    #optIds = request.GET.get('oids')
    #qetQryList = request.GET.get('qlist')
    #optHeader = request.GET.get('optHeader')

    # Set default mode
    mode = 'AND'

    if request.GET.get('mode'):
        mode = request.GET.get('mode') 

    print('QUERY STRING')
    pprint(queryString)

    # Turn list of values into list of Q objects
    if queryString:
        asset = Asset.objects.all().order_by('fileName')

        searchResults = SearchAssetsOptions(queryString, asset, mode)

    #Pagination
    paginator = Paginator(searchResults, quanPerPage)
    page_number = request.GET.get('page', 1)
    try:
        searchResults = paginator.get_page(page_number)
    except PageNotAnInteger:
        searchResults = paginator.get_page(page_number)
    except EmptyPage:
        searchResults = paginator.get_page(paginator.num_pages)
    
    print('PAGINATION/QUERY')
    print(queryString)
    print(searchResults)

    # pprint(request.GET.dict())
    devOut = request.GET.dict()
    context['searchResults'] = searchResults
    context['devOut'] = devOut
    context['queryString'] = queryString
    static_asset_filesnames = {'javascript':'search.js', 'styles':'search.css', 'vuejs':'search_vue.js'}
    context['static_asset_filesnames'] = static_asset_filesnames

    optionGroups = []
    optionsData = Option.objects.all().values('groupName').distinct().order_by('groupName')
    for opt in optionsData:
        optionGroups.append(dict(groupName=opt['groupName']))
    #print('SearchAssets:: OPTIONS DATA')
    #pprint(optionGroups) 
    context['optionGroups'] = optionGroups 


    return render(request, 'search/search.html', context)

"""
    Displays a file asset and its attributes
    on a template at search/asset.html

    NOTE: Use VueJS to add functionality to this
"""
def search_by_filename(request):
    context = {}
    assetDict = {}
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        file_name = request.POST.get('filename')
        print('POST:')
        pprint(request.POST.get('filename'))
        
        asset = Asset.objects.get(fileName=file_name)
        #asset = Asset.objects.filter(fileName=file_name)
        print('ASSET')
        pprint(asset)
 
        serializedAsset = AssetSerializer(asset)
        #assetDict['human_readable_id'] = serializedAsset.data['id']
        assetDict['id'] = serializedAsset.data['id']
        #assetDict['fileName'] = serializedAsset.data['fileName']
        assetDict['search_string'] = serializedAsset.data['search_string']
        assetDict['timestamp'] = serializedAsset.data['timestamp']
        assetDict['options'] = serializedAsset.data['options']

        context['asset'] = asset
        context['assetDict'] = assetDict

    return render(request, 'search/asset.html', context)

"""
    This returns a JSON object of all the values for 
    a given Asset Option Group based on the optionGroupName
    in the request object.

    This seems to be a duplicate of def get_option_group_values(request):

"""
def ajax_option_group_values(request):
    data = []
    optionGroupName = request.GET['optionGroupName']
    optionGroupName.replace("%20", " ")
    options  = Option.objects.filter(groupName=optionGroupName).order_by('definition')
   
    for dat in options:
        # Make a list of dictionaries to be converted to JSON
        # safe=False must be set for JsonResponse(data, safe=False) to work 
        # with a list of dictionaries
        data.append({'id':dat.id,'groupName': dat.groupName, 'definition':dat.definition})

    return JsonResponse(data, safe=False) 

def SearchAssetsOptions(urlQuery, asset, mode="AND"):
    '''
       NOTE: from django.db.models import Q # filter using operators '&' or '|'
             https://docs.djangoproject.com/en/3.1/topics/db/queries/#complex-lookups-with-q-objects
    '''
    searchResults = ''
    optionHeaders = ''

    if urlQuery:
        # Split out the main search modes
        optIdList = urlQuery.split(",")
        # init the query var
        query = Q() 
        excludeQuery = Q()
        andedOrQuery = Q()
        andedOptHdrQuery = Q()
        andedOrOptHdrQuery = Q()
        excludeOptHdrQuery = Q()
        excludeOrOptHdrQuery = Q()

        for optId in optIdList:       
            #if mode == "OR":
            #    query |= Q(search_string__exact=optId)
            if mode == "AND":
                """
                ///////////////////////////////////////////////////////////

                Handle Asset Option Headers which are preceeded with ^ when AND'd
                and preceeded with ^~ for AND'd OR
                eg.
                ^Door%20Style%20Name^Accessories%20by%20Room^~Art%20File^~Art%20for%20Everyday

                ///////////////////////////////////////////////////////////
                """
                """
                Split them out and treat item(s) as AND'd unless the
                item is preceeded by ~ in which case it is an OR'd
                """

                if optId[0] == '^' :
                    #    ^ indicates an Asset Option Header
                    optionHeaderList = optId.split("^")
                    print('optionHeaderList', optionHeaderList)
                    for optHdr in optionHeaderList:
                        if optHdr :
                            # If this is an AND's-OR item
                            if optHdr[0] == '~':
                                # strip off the prefix
                                optHdr = optHdr.replace("~","")
                                andedOrOptHdrQuery |= Q(options__groupName=optHdr)
                            
                             # If this is an excluded AND item
                            #if optHdr[0] == ':':
                            #    # strip off the prefix
                            #    optHdr = optHdr.replace(":","")
                            #    excludeOptHdrQuery &= Q(options__groupName=optHdr)
                            
                            # If this is an excluded-OR item
                            if optHdr[0] == '|':
                                # strip off the prefix
                                optHdr = optHdr.replace("|","")
                                excludeOrOptHdrQuery |= Q(options__groupName=optHdr)

                            # Else this is an AND item
                            else:
                                andedOptHdrQuery &= Q(options__groupName=optHdr)

                    query &= andedOptHdrQuery
                    query &= andedOrOptHdrQuery
                    excludeQuery  &= excludeOptHdrQuery
                    excludeQuery  &= excludeOrOptHdrQuery

                    continue


                """
                ///////////////////////////////////////////////////////////

                Handle Option IDs which are preceeded with "," when AND'd
                and preceeded with ~ for AND'd OR
                and preceeded with - when EXCLUDED
                eg.
                ,1021,1275,1862,1863,~2783~3032~1865,-1344,-1343,-1916

                ///////////////////////////////////////////////////////////
                """

                """
                Handle AND'd ORs for option IDS which are 
                separated by ~
                """
                if optId[0] == '~' :
                    orOptIdList = optId.split("~")
                    for orOptId in orOptIdList:
                        if orOptId :
                            orOptId.replace('~','')#remove the tilde
                            orOptId = '-'+orOptId+'-'
                            andedOrQuery |= Q(search_string__contains=orOptId)
                    query &= andedOrQuery
                    continue

                """ 
                EXCLUSIONS HANDLING
                NOTE: There a 2 ways of handleing the exclusions one is to
                      default to simple AND'd exclusions in the second els:
                      below.
                      The other way is with prefixes of "-:" and "-|" for 
                      AND and OR respectivly. See code below.
                      The default is what is currently programmed into the
                      Admin UI.
                """
                print('PRE-IF OPT ID:' + optId)
                if optId[0] == '-' :
                    # ADDITIONAL ALTERNATIVE WAY TO HANDLE EXCLUSIONS
                    # WITH PREFIXES OF   -:  and -|   AND  and OR
                    # This way is NOT YET programmed into the front end
                    # VueJS Admin UI Panel.
                    if '-|' in optId:
                        for opt in optId.split('-|'):
                            # '~-' is plit out.
                            # Remove remaining neg sign
                            #opt = opt.replace('-|','')
                            if(opt != ''):
                                optStr = '-'+opt+'-'
                                print('IF: -| OPT ID:' + opt, optStr)
                                excludeQuery |= Q(search_string__contains=optStr)
                            continue
                    elif '-:' in optId:
                        for opt in optId.split('-:'):
                            # '-:' is split out.
                            if(opt != ''):
                                optStr = '-'+opt+'-'
                                print('ELIF: -: OPT ID:' + opt, optStr)
                                excludeQuery &= Q(search_string__contains=optStr)  
                            continue  

                    # DEFAULT AND'd EXCLUSIONS
                    # This way IS programmed into the front end
                    # VueJS Admin UI Panel.
                    else :
                        #remove minus sign
                        optStr = optId.replace('-','') 
                        print('ELSE: OPT ID:' + optId, optStr)
                        # Flank with hyphens
                        optStr = '-'+optStr+'-'
                        # remove the minus sign with optId[1:]
                        excludeQuery &= Q(search_string__contains=optStr)
                        continue

                else:
                    # Finally handle the normal AND'd  IDs
                    optId = '-'+optId+'-'
                    query &= Q(search_string__contains=optId)


        count = asset.filter(query).exclude(excludeQuery).count()
        #searchResults = asset.filter(query).exclude(excludeQuery)[:300]
        searchResults = asset.filter(query).exclude(excludeQuery)

        print("SEARCH::views:query " + str(count))
        print("SEARCH::views:count" + str(searchResults.query))
        data = {}
        data["searchResults"] = searchResults
        data["count"] = count
        return data

"""
    This returns a JSON object of all the values for 
    a given Asset Option Group based on the optionGroupName
    in the request object.
"""
def get_option_group_values(request):
    data = []
    optionGroupName = request.GET['optionGroupName']
    options  = Option.objects.filter(groupName=optionGroupName).order_by('definition')
   
    for dat in options:
        # Make a list of dictionaries to be converted to JSON
        # safe=False must be set for JsonResponse(data, safe=False) to work 
        # with a list of dictionaries
        data.append({'id':dat.id,'groupName': dat.groupName, 'definition':dat.definition})

    return JsonResponse(data, safe=False)







