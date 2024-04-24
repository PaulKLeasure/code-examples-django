from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from rest_framework.authtoken.models import Token
from django.views.decorators.csrf import csrf_exempt
from django.db.models.functions import Cast
from django.core.exceptions import ObjectDoesNotExist
from .models import FilterGroupItem, FilterGroup, Filter
from core.models  import Option
from core.serializers import OptionSerializer
from .serializers import AssetFilterNavSerializer, AssetFilterNavGroupSerializer, AssetFilterNavGroupItemSerializer
#from .functions import get_item
from pprint import pprint
import json
from operator import itemgetter
import traceback

#  /api/filter-nav/?mach_name=<mach_name>
#  /api/filter-nav/?id=<id>
# 
#  returns: json data
#
@api_view(["POST","GET","PUT","DELETE"])
@permission_classes([IsAuthenticated])
@csrf_exempt
def filter_nav(request):
    #payload = json.loads(request.body.decode("utf-8"))
    user = get_user_from_token(request=request)
    # READ ACCESS OPEN with API Auth Token
    if(request.method == "GET"):
        return getFilterNavs(request)
    # "POST","PUT","DELETE" Only authorized for user is admin
    if not user.is_admin:
        context = {"response_code": 401, "message": "Not authorized! " + user.username + " is not an admin.",
                   "success": "false"}
        return JsonResponse(context, safe=False)
    if(request.method == "POST"):
        return createFilterNav(request)
    if(request.method == "PUT"):
        return updateFilterNav(request)
    if(request.method == "DELETE"):
        return deleteFilterNav(request)


# /api/filter-nav/group/ 
# /api/filter-nav/group/?id=<id>
# 
#  returns: json data
#
@api_view(["POST","GET","PUT","DELETE"])
@permission_classes([IsAuthenticated])
@csrf_exempt
def filter_group_nav(request):
    #payload = json.loads(request.body.decode("utf-8"))
    user = get_user_from_token(request=request)
    # READ ACCESS OPEN with API Auth Token
    if(request.method == "GET"):
        return getFilterNavGroup(request)
    # "POST","PUT","DELETE" Only authorized for user is admin
    if not user.is_admin:
        context = {"response_code": 401, "message": "Not authorized! " + user.username + " is not an admin.",
                   "success": "false"}
        return JsonResponse(context, safe=False)
    if(request.method == "POST"):
        return createGroupFilterNav(request)
    if(request.method == "PUT"):
        return updateFilterNavGroup(request)
    if(request.method == "DELETE"):
        return deleteFilterNavGroup(request)


"""
DELETE  Filter Navigation Object
  curl -X "DELETE" api/filternav?id=<id>
"""
def deleteFilterNav(request):
    REST_VERB = request.method
    mode = request.GET.get('mode')
    error = False
    isDeleted = False
    id = False
    id = request.GET.get('id')
    data = None
    success = False
    if(id):
        try:
            # Delete all the group items, then all the groups, then the filter
            filterObj = Filter.objects.get(id=id)
            data = processData(filterObj.id)
            for group in data["filterGroups"]:
                filterGroupItems = FilterGroupItem.objects.filter(parentGroup=group["id"])
                for filterGrpItem in filterGroupItems:
                    filterGrpItem.delete()
                FilterGroupObj = FilterGroup.objects.get(pk=group["id"])
                FilterGroupObj.delete()
            filterObj.delete()
            success = True
            isDeleted = True
        except ObjectDoesNotExist:
            success = False       
            error = "Error: " + str(id) + " cannot be deleted becasue it does not exist in database!" 
    else:
        error = "Error: id parameter missing!"
        sucess = False 

    metadata = {
        'verb': REST_VERB,
        'mode': mode,
        'success': success,
        'uri': request.META['HTTP_HOST']+request.META['PATH_INFO']+request.META['QUERY_STRING'],
        'isDeleted': isDeleted
        }
    if error:
        metadata["error"] = error

    return JsonResponse({'metadata': metadata, 'data': data}, safe=False)

"""
DELETE  Filter Navigation Group
  curl -X "DELETE" api/filternav?id=<id>
"""
def deleteFilterNavGroup(request):
    REST_VERB = request.method
    error = False
    isDeleted = False
    mode = ""
    gid = False
    itemId = False
    if "mode" in request.GET:
        mode = request.GET.get("mode")
    if "gid" in request.GET:
        gid = int(request.GET.get("gid"))
    if "itemId" in request.GET:
        itemId = request.GET.get("itemId")
    data = None
    success = False
    if itemId and mode == "item-remove":
        try:
            filterItemObj = FilterGroupItem.objects.get(pk=itemId)
            filterItemObj.delete()
            success = True
            isDeleted = True
        except ObjectDoesNotExist:
            success = False       
            error = "Error: " + str(itemId) + " cannot be deleted becasue it does not exist in database!" 
    # This case is Group delete
    if gid and mode != "item-remove" :
        try:
            # Start with removing the filter groups items
            filterGroupItems = FilterGroupItem.objects.filter(parentGroup=gid)
            for filterGrpItem in filterGroupItems:
                filterGrpItem.delete()
            # Then delete the filter group
            AssetFilterGroup = FilterGroup.objects.get(pk=gid)        
            ParentFilter = AssetFilterGroup.parentFilter
            AssetFilterGroup.delete()
            success = True
            isDeleted = True
        except ObjectDoesNotExist:
            success = False       
            error = "Error: " + str(gid) + " cannot be deleted becasue it does not exist in database!" 

    metadata = {
        'verb': REST_VERB,
        'mode': mode,
        'success': success,
        'uri': request.META['HTTP_HOST']+request.META['PATH_INFO']+request.META['QUERY_STRING'],
        'isDeleted': isDeleted
        }
    if error:
        metadata["error"] = error
    return JsonResponse({'metadata': metadata, 'data': data}, safe=False)

def createFilterNav(request):
    success = False
    error = False
    REST_VERB = request.method
    filterData = {}
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    try:
        # Create Object
        filterObject = Filter(
            Name = body["Name"], 
            Description = body["Description"], 
            LocationPath = body["LocationPath"],  
            mach_name = body["mach_name"], 
            Enabled = body["Enabled"], 
            Sort = body["Sort"], 
        )
        # Set all the new options
        for fGrp in body["filterGroups"]:
            gid = int(fGrp["id"])
            print("FG ID: " + str(gid))
            if isinstance(gid, str) :
                gid = int(gid)
            filterGroupObject = FilterGroup.objects.get(pk=gid)
            filterObject.filterGroups.add(filterGroupObject)
        # Commit the change
        filterObject.save()
        filterSerialized = AssetFilterNavSerializer(filterObject, many=False)
        filterData = filterSerialized.data
        success = True    
    except: 
        error = "Failed to fetch Filter object"
        success = False
        count = 0
        print("ERROR::" + error)

    metadata = {
        'verb': REST_VERB,
        'success': success,
        'endpoint': request.META['HTTP_HOST']+request.META['PATH_INFO']+"?"+request.META['QUERY_STRING']
        }
    if error:
        metadata["error"] = error

    return JsonResponse({'metadata': metadata, 'data': filterData}, safe=False)

def updateFilterNav(request):
    success = False
    error = False
    REST_VERB = request.method
    filterData = {}
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    int_id = int(body["id"])
    try:
        filterObj = Filter.objects.get(pk=int(body["id"]))
        filterObj.Name = body["Name"]
        filterObj.Description = body["Description"]
        filterObj.LocationPath = body["LocationPath"]
        filterObj.mach_name = body["mach_name"]
        filterObj.Enabled = body["Enabled"]
        filterObj.Sort = body["Sort"]
        groups =  []
        for filterGroup in body["filterGroups"]:
            fgid = filterGroup["id"]
            groupSerializedData = processFilterNavGroupData(fgid)
            groups.append(groupSerializedData)            
        filterObj.save()
        filterSerialized = AssetFilterNavSerializer(filterObj, many=False)
        filterData = filterSerialized.data
        filterData["filterGroups"] = groups
        success = True    
    except: 
        error = "Failed to fetch Filter object"
        success = False
        count = 0
        print("ERROR::" + error)

    metadata = {
        'verb': REST_VERB,
        'success': success,
        'endpoint': request.META['HTTP_HOST']+request.META['PATH_INFO']+"?"+request.META['QUERY_STRING']
        }
    if error:
        metadata["error"] = error

    return JsonResponse({'metadata': metadata, 'data': filterData}, safe=False)


def getFilterNavs(request):
    success = False
    css_style = ""
    error = False
    isList = False
    REST_VERB = request.method
    data = {}
    data["Name"] = ""
    data["Description"] = ""
    data["LocationPath"] = ""
    data["filterGroups"] = []
    data["mach_name"] = ""
    data["Enabled"] = True
    data["Sort"] = 0
    page = 1
    if "page" in request.GET:
        page = request.GET["page"]
    count = 0
    if "mode" in request.GET and request.GET["mode"] == 'filter':
        try:
            if "mach_name" in request.GET :
                mach_key = request.GET["mach_name"]
                filterObj = Filter.objects.get(mach_name=mach_key)
                data = processData(filterObj.id)
            elif "location_path" in request.GET :
                loc_path = request.GET["location_path"]
                filterObj = Filter.objects.get(LocationPath=loc_path)
                data = processData(filterObj.id)
            elif "id" in request.GET :
                print("ID: "+request.GET["id"])
                int_id = int(request.GET["id"])
                data = processData(int_id)
            success = True
            css_style = 'asset-filter-nav-' + str(data["id"])
            count = 1
        except Exception as e: 
            message = traceback.format_exc()
            print(message)
            error = "Failed to fetch Filter Group object" + message
            success = False
            count = 0 

    if "mode" in request.GET and request.GET["mode"] == 'index':
        filterObjects = Filter.objects.all().order_by('Sort','Name').values()
        filterNavs = []
        try:
            for filterObj in filterObjects:
                print("Filter OBJ")
                fid = filterObj["id"]
                print("FILTER OBJECT ID:" + str(fid))
                filterNavs.append(processData(fid))
            success = True
            css_style = 'asset-filter-nav-index'
        except Exception as e: 
            message = traceback.format_exc()
            print(message)
            error = "Failed to fetch Filter Group object" + message
            success = False
            count = 0       
        count = len(filterNavs)
        isList = True
        data['filterNavs'] = filterNavs

    metadata = {
        'verb': REST_VERB,
        'page': page,
        'success': success,
        "style": css_style,
        'endpoint': request.META['HTTP_HOST']+request.META['PATH_INFO']+"?"+request.META['QUERY_STRING'],
        'is_list': isList, 
        'count': count
        }
    if error:
        metadata["error"] = error

    return JsonResponse({'metadata': metadata, 'data': data}, safe=False)

def createGroupFilterNav(request):
    success = False
    error = False
    REST_VERB = request.method
    filterData = {}
    groupItems = []
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    filterGroupData = {}
    try:
        # Create Object
        pid = body["parentId"]
        if isinstance(pid, str):
            pid = int(pid)
        if 'Description' in body:
            descr = body["Description"]
        else:
            descr = ""
        FilterObj = Filter.objects.get(pk=pid)
        groupSort = body["Sort"]
        if isinstance(groupSort, str):
            groupSort = int(groupSort)

        filterGroupObject = FilterGroup(
            Name = body["Name"], 
            Description = descr,  
            Sort = int(body["Sort"]), 
            parentFilter = FilterObj
        )
        # Commit the change
        filterGroupObject.save()
        filterGroupSerialized = AssetFilterNavGroupSerializer(filterGroupObject, many=False)
        filterGroupData = filterGroupSerialized.data
        filterGroupData["groupItems"] = groupItems
        success = True    
    except Exception as e: 
        message = traceback.format_exc()
        print(message)
        error = "Failed to fetch Filter Group object" + message
        success = False
        count = 0
        
    metadata = {
        'verb': REST_VERB,
        'success': success,
        'endpoint': request.META['HTTP_HOST']+request.META['PATH_INFO']+"?"+request.META['QUERY_STRING']
        }
    if error:
        metadata["error"] = error


    return JsonResponse({'metadata': metadata, 'data': filterGroupData}, safe=False)

def updateFilterNavGroup(request):
    success = False
    error = False
    REST_VERB = request.method
    filterGroupData = {}
    data = {}
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    print("-------------------------")
    print("  FILTER GROUP UPDATE ")
    print("-------------------------")
    pprint(body)
    print("ID: "+str(body["id"]))
    int_id = int(body["id"])
    
    try:
        gid = body["id"]
        if isinstance(gid, str):
            gid = int(gid)
        pid = body["parentFilter"]
        if isinstance(pid, str):
            pid = int(pid)
        FilterObj = Filter.objects.get(pk=pid)
        groupSort = body["Sort"]
        if isinstance(groupSort, str):
            groupSort = int(groupSort)
        filterGroupItems = body["filterGroupItems"]
        filterGroupObj = FilterGroup.objects.get(pk=gid)
        parentFilterObj = Filter.objects.get(pk=pid)
        #pprint(filterGroupObj)
        #print("=== UPDATE GROUP DATA filterObj  ===>")
        filterGroupObj.Name = body["Name"]
        filterGroupObj.Description = body["Description"]
        filterGroupObj.parentFilter = parentFilterObj 
        filterGroupObj.Sort = groupSort
        filterGroupObj.selectionElement = body["selectionElement"]
        existingGroupItemCoreOptionIds =  []

        existingGroupItemObjects = FilterGroupItem.objects.filter(parentGroup=filterGroupObj)
        
        #build list of existing core items to avoid duplicates
        for existingGroupItemObj in existingGroupItemObjects:
            #pprint(existingGroupItemObj.coreOption.id)
            existingGroupItemCoreOptionIds.append(existingGroupItemObj.coreOption.id)

        print("existingGroupItemCoreOptionIds Core Option IDs")
        pprint(existingGroupItemCoreOptionIds)

        #for co in filterGroupItems:
        #    if co["coreOption_id"] not in coreOptionIds:
        #        print(str(co["coreOption_id"]))
        #        coreOptionIds.append(co["coreOption_id"])



        # clear the filter group items 
        for groupItem in filterGroupItems:
            print("filterGroupItems")
            pprint(groupItem)
            # .save() performs intelligent UPDATE or INSERT
            # So build each item and use .save()
            print("MATCHER: "+str(groupItem["coreOption_id"])+"<-->")
            

            print("---- THIS FAR ---")
            #existingGroupItemCoreOptionIds.append(co["coreOption_id"])
            print("=== Core Option IDs ===")
            pprint(existingGroupItemCoreOptionIds)
            print('groupItem')
            pprint(groupItem)
            coreOptionObject = Option.objects.get(pk=int(groupItem["coreOption_id"]))
            pprint(coreOptionObject)
            if len(groupItem["Name"]) > 3 :
                groupItemTitle = groupItem["Name"]
            else:
                groupItemTitle = coreOptionObject.definition
            try: 
                groupItemObject = FilterGroupItem(
                    Name = groupItem["Name"],
                    Description = groupItem["Description"],
                    Sort = int(groupItem["Sort"]),
                    coreOption = coreOptionObject,
                    parentGroup = filterGroupObj
                )
                print(groupItemObject)
                #
                if int(groupItem["coreOption_id"]) in existingGroupItemCoreOptionIds:
                    if int(groupItem["id"]):
                        groupItemObject.id = groupItem["id"]
                        groupItemObject.save(force_update=True)
                else:
                    groupItemObject.save()
                    existingGroupItemCoreOptionIds.append(groupItem["coreOption_id"])

                
            except Exception as e: 
                message = traceback.format_exc()
                print(message)
                error = "Failed to fetch Filter Group object" + message
                success = False
                count = 0

        filterGroupObj.save()
        # #print("=== SERIALIZED UPDATE DATA filterObj  ===>")
        # filterGroupSerialized = AssetFilterNavGroupSerializer(filterGroupObj, many=False)
        # data = filterGroupSerialized.data
        # #filterData["filterGroups"] = groups
        # pprint(data)
        # success = True    
    except Exception as e: 
        message = traceback.format_exc()
        print(message)
        error = "Failed to fetch Filter Group object" + message
        success = False
        count = 0

    metadata = {
        'verb': REST_VERB,
        'success': success,
        'endpoint': request.META['HTTP_HOST']+request.META['PATH_INFO']+"?"+request.META['QUERY_STRING']
        }
    if error:
        metadata["error"] = error

    return JsonResponse({'metadata': metadata, 'data': data}, safe=False)


def getFilterNavGroup(request):
    success = False
    css_style = ""
    error = False
    isList = False
    REST_VERB = request.method
    data = {}
    page = 1
    if "page" in request.GET:
        page = request.GET["page"]
    count = 0
    #if "mode" in request.GET:
    #    print("MODE: "+request.GET["mode"])

    if "create" in request.GET and "parentId" in request.GET:
        #print("----------------------")
        #print("  CREATE GROUP")
        #print("----------------------")
        data = {}
        data["Name"] = ""
        data["Description"] = ""
        if "parentId" in request.GET:
            data["parentFilter"] = request.GET["parentId"]
        data["Sort"] = 0
        try:
            int_parentId = int(request.GET["parentId"])
            #data = processGroupsPerFilterNav(int_parentId) 
            success = True
            css_style = 'asset-filter-nav-group-' + str(filterObj.id)
            count = null
        except: 
            error = "Failed to fetch Filter Group Object by parentId"
            success = False
            count = 0
    elif "parentId" in request.GET:
        #print("----------------------")
        #print(" GROUPS BY PARENT ID")
        #print("----------------------")
        try:
            int_parentId = int(request.GET["parentId"])
            data = processGroupsPerFilterNav(int_parentId) 
            success = True
            css_style = 'asset-filter-nav-group-' + str(filterObj.id)
            count = null
                  
        except: 
            error = "Failed to fetch Filter Group Object by parentId"
            success = False
            count = 0
    elif "id" in request.GET:
        try:
            int_id = int(request.GET["id"])
            filterObj = FilterGroup.objects.get(pk=int_id)
            success = True
            css_style = 'asset-filter-nav-group-' + str(filterObj.id)
            count = 1
            data = processFilterNavGroupData(int_id)
        except: 
            error = "Failed to fetch Filter Group Object by ID"
            success = False
            count = 0
    else:
        # is index of groups
        filterGroupObjects = FilterGroup.objects.all().order_by('Sort','Name').values()
        #pprint(filterGroupObjects)
        filterGroupNavs = []
        try:
            data = processGroupsIndexData(filterGroupObjects)
            success = True
            css_style = 'asset-filter-nav-group-index'
        except: 
            error = "Failed to fetch index of Filter Groups"
            success = False
            count = 0        
        count = len(data)
        isList = True
    
    metadata = {
        'verb': REST_VERB,
        'page': page,
        'success': success,
        "style": css_style,
        'endpoint': request.META['HTTP_HOST']+request.META['PATH_INFO']+"?"+request.META['QUERY_STRING'],
        'is_list': isList, 
        'count': count
        }
    if error:
        metadata["error"] = error
    return JsonResponse({'metadata': metadata, 'data': data}, safe=False)

# =============================================================
# Processing Functions
# =============================================================

def processData(fid):
    #print("------------------------------------")
    #print("     processData(filterObjIn)   ")
    #print("------------------------------------")   
    filterObj = Filter.objects.get(pk=fid)
    filterSerialized = AssetFilterNavSerializer(filterObj, many=False)
    s_data = filterSerialized.data
    s_data["filterGroups"] = processGroupsPerFilterNav(filterObj.id)
    print("==========[][][][][][ =============")
    print("def processData(filterObjIn, groupObjsIn):")
    #pprint(s_data)
    return s_data

def processGroupsIndexData(groups):
    #print("---------------------------------------")
    #print("   processGroupsIndexData(groups):     ")
    #print("---------------------------------------")
    dat = []
    for group in groups:
        gid = int(group["id"])
        groupData = processFilterNavGroupData(gid)
        dat.append(json.loads(json.dumps(groupData)))
    return dat

def processGroupsPerFilterNav(fid):
    #print("---------------------------------------")
    #print("processGroupsPerFilterNav(filterObjIn)")
    #print("---------------------------------------")
    groups = []
    #fid = filterObjIn.id
    groupObjs = FilterGroup.objects.filter(parentFilter=fid).order_by('Sort','Name').values()
    #pprint(groupObjs)
    for groupObj in groupObjs:
        gid = groupObj["id"]
        groupSerializedData = processFilterNavGroupData(gid)
        groups.append(groupSerializedData)
    return groups

def processFilterNavGroupData(id):
    filterGroupObj = FilterGroup.objects.get(id=int(id))
    return processFilterGroupByObject(filterGroupObj)

def processFilterGroupByObject(groupObj):
    print("------------------------------------")
    print("processFilterGroupByObject(groupObj)")
    print("------------------------------------")
    groupSerialized = AssetFilterNavGroupSerializer(groupObj, many=False)
    groupSerializedData = groupSerialized.data
    pprint(groupSerializedData)
    groupSerializedData["filterGroupItems"] = []
    gid = groupSerializedData["id"]
    GroupItems = FilterGroupItem.objects.filter(parentGroup=gid).order_by('Sort','Name').values()
    groupedItems = []
    for groupItem in GroupItems:
        groupItem["coreOption"] = {}
        groupItem["coreOption"] = processCoreItem(groupItem)   
        print(" ======>  groupItem  ==== ")
        #pprint(groupItem)
        groupedItems.append(groupItem)   
    groupSerializedData["filterGroupItems"]=groupedItems   
    return groupSerializedData

def processCoreItem(groupItem):
    #print("------------------------------------")
    #print("     processCoreItem(groupItem)     ")
    #print("------------------------------------")
    #pprint(groupItem)
    coid = int(groupItem["coreOption_id"])
    coreItem = Option.objects.get(id=coid)
    coreItemSerialized = OptionSerializer(coreItem, many=False)
    return coreItemSerialized.data



def get_user_from_token(request):
    token_key = request.META.get('HTTP_AUTHORIZATION').replace("Token ", "")
    user = Token.objects.get(key=token_key).user
    return user
