from .models import IvaultLog
from .serializers import IvaultLogSerializer
from core.models import Category, Asset, Option, ivault_t_search, ivault_t_options, ivault_t_vals,BatchTagHistory
from django.core.exceptions import ObjectDoesNotExist
import json
from django.http import HttpRequest, HttpResponse, JsonResponse
from pprint import pprint
from datetime import datetime
from django.db.models import Q # filter using operators '&' or '|'

import pytz

#  EXAMPLE  date = d.now()
#  EXAMPLE  print('>>>>  TIME <<<<<')
#  EXAMPLE  print(date.strftime("%Y-%m-%d %H:%M:%S"))

# from iv_logger.functions import  insertFileNameWhenEmpty
"""
Insert filename when empty
"""
def insertFileNameWhenEmpty():
    Logs = IvaultLog.objects.filter(filename=str('empty'))
    for log in Logs:
        # extract filename from log.data
        filename = extractFilenameFromLogData(log)
        if filename:
            print('FILENAME:'+filename)
            log.filename = filename
            log.save()

def extractFilenameFromLogData(log):
    if 'FILENAME:' in log.data:
        segments = log.data.split(",")
        for seg in segments:
             if 'FILENAME:' in seg:
                 filename = seg.replace('FILENAME:','').strip()
                 return filename
    if 'CREATE/UPLOAD Option |' in log.data:
        segments = log.data.split(",")
        filename = segments[4].strip()
        return filename
    if 'CREATE S3 upload |' in log.data:
        segments = log.data.split(" ")
        filename = segments[7].strip()
        return filename
    if 'TAGBOT file:' in log.data:
        segments = log.data.split("|")
        for seg in segments:
             if 'TAGBOT file:' in seg:
                 filename = seg.replace('TAGBOT file:','').strip()
                 return filename
    #print("FAILED TO FIND:"+str(log.data))
    return False




"""
Ensure Legacy Asset Has Log
"""
def ensureLog(objectInput):
    #print('============ ENSURE LOG ===============')
    objInputDict = {}
    if(objectInput):
        for attr, value in objectInput.__dict__.items():
            if(attr != "_state"):
                #print("ATTR:" + attr+ " : "+ str(value))
                objInputDict[attr] = str(value)

    # Try with filename column first        
    #ivaultLogData = queryLogsByFilename(objInputDict["fileName"])
    ivaultLogData = queryLogByFilenameColumn(objInputDict["fileName"])
    if(ivaultLogData):
        pass
    else:
        commitLogEntryToDatabase("API:legacy log", "legacy log", "Asset", objectInput)


"""
Get asset logs by filename
"""
def getHumanReadableLogsByAssetFilename(filename=None):
    # context = {}
    data = []
    # Special function to attempt fastest query first
    #ivaultLogData = queryLogsByFilename(filename)
    ivaultLogData = queryLogByFilenameColumn(filename)

    if(ivaultLogData):
        serializedLogs = IvaultLogSerializer(ivaultLogData, many=False)
        #pprint(ivaultLogData)
        for logObj in ivaultLogData :
            #print('========== LOG OBJ  ============')
            #print('getHumanReadableLogsByAssetFilenam('+filename+')')
            #pprint(logObj.data)
            #print('========== BEFOR FUNCTION CALL ============')
            logList = inturprateAssetLogToHumanReadable(logObj, logObj.logged_user)
            #print('========== AFTER FUNCTION CALL ============')
            #pprint(logList)
            for x in logList:
                data.append(x)

            # using naive method
            # to remove duplicated 
            # from list 
            resList = []
            for i in data:
                if i not in resList:
                    resList.append(i)
            data = resList

            #print('========= DATA ===========')
            #pprint(data)

    return data

"""
Log Inturprater for Human readability
This is for displaying the logs on the Asset detail
page in the Admin UI
"""
def inturprateAssetLogToHumanReadable(logObj, user):
    logList = []
    
    if logObj.data.find('SEARCH_STRING') != -1 :
        logList = inturprateSearchString(logObj, user)

    if logObj.data.find('CREATE/UPLOAD Option') != -1 :
        logList = logList + inturprateOptionAtUpload(logObj, user)

    if logObj.data.find('S3 upload') != -1 :
        logList = logList + inturprateS3Upload(logObj, user)

    return logList


def inturprateOptionAtUpload(logObj, user):
    #print(' === inturprateOptionAtUpload OPTION at UPLAOD LOG STRING =====')
    log_lines = []
    classes = ["log-line"]
    timeString = "(timeStamp unknown)"
    styleTextSuccess = "upload-success"
    styleTextAction = "uplaoded-tag"
    actionText = "tag added "
    timeString = "(timeStamp unknown)"
    logMode = ""

    if logObj.data.find('log_timestamp:') != -1:
        timeStringList = logObj.data.split('log_timestamp:')
        timeString = timeStringList[1].strip()
    
    if "default" not in logObj.mode:
        logMode = logObj.mode

    logString = logObj.data.replace('CREATE/UPLOAD Option |', '')
    logStringList = logString.split(',')
    oid = logStringList[0].replace("ID:","").strip()
    grp = logStringList[1].replace("GROUPNAME:","").strip()
    def1 = logStringList[2].replace("DEFINITION:","").strip()
    filename = logObj.filename
    if 'empty' in filename:
        filename = logStringList[4]

    style_classes = "username added-option"

    lineStr = '<span class="'+style_classes+'">'+user +'</span> <span class="added-option"><span class="log-mode">'+logMode+'</span><span class="log-action">added</span> '+'<span class="option-id">('+oid+')</span>  <span class="option-title">'+ grp +'::'+def1+' <span style="color:#000">&nbsp; &nbsp; &#8594; &nbsp; '+ filename +'</span></span> <span class="timestamp">'+timeString+'</span></span>'
    #print(lineStr)
    log_lines.append({ "log_id": logObj.id, "log":lineStr })
    return log_lines


def inturprateS3Upload(logObj, user):
    log_lines = []
    timeString = "(timeStamp unknown)"
    styleTextSuccess = "upload-success"
    styleTextAction = "uplaoded-s3"
    actionText = "S3 upload"

    timeString = "(timeStamp unknown)"

    if logObj.data.find('log_timestamp:') != -1:
        timeStringList = logObj.data.split('log_timestamp:')
        timeString = timeStringList[1].strip()

    if logObj.data.find('FAILED') != -1 :
        styleTextSuccess = "upload-failed"
        styleTextAction = "upload-s3-failed"

        actionText = "S3 Failed"

    
    logString = logObj.data.replace('CREATE S3 upload |', '')
    logString = logString.split(',')[0].strip()

    

    lineStr = '<span class="username">'+user +'</span> <span class="'+styleTextSuccess+'"><span class="log-action">' + actionText +'</span> '+'<span class="s3-log-text">' + logString + '</span> <span class="timestamp">'+timeString+'</span></span>'
    #print(lineStr)
    log_lines.append({ "log_id": logObj.id, "log":lineStr })
    return log_lines



def inturprateSearchString(logObj, user):
    #print('============= INSIDE inturprateSearchString  ==============')
    parts = logObj.data.split(",")
    log_id = logObj.id
    idx = "none"
    log_lines = []
    classes = ["log-line"]
    splitIndex = None
    timeString = "(timeStamp unknown)"
    logMode = '';

    if "default" not in logObj.mode:
        logMode = logObj.mode

    if logObj.data.find('log_timestamp:') != -1:
        timeStringList = logObj.data.split('log_timestamp:')
        timeString = timeStringList[1].strip()

    for idx, part in enumerate(parts):
        #print(part)
        if part.find("BEFORE UPDATE") != -1:
            print('FOUND ---('+str(idx)+') '+part)
            splitIndex = idx
            #print('splitIndex=',splitIndex)
            break
    
    logCurrentAction = parts[0:splitIndex]
    logPreviousAction = parts[splitIndex:]
    
    dataCurrent = {}
    for piece in logCurrentAction:
        pc = piece.split(":",1)
        if len(pc) > 1:
            key = pc[0].strip()
            dat = pc[1].strip()
            if key and dat:
                dataCurrent[key] = dat

    dataPrevious = {}
    for piece in logPreviousAction:
        pc = piece.split(":",1)
        if len(pc) > 1:
            key = pc[0].strip()
            dat = pc[1].strip()
            if key and dat:
                dataPrevious[key] = dat

    optionsCurrent = dataCurrent['SEARCH_STRING'].split('--')
    #print('------------inturprateSearchString()----------')
    # Remove any empty elements from the list
    optionsCurrent = [i for i in optionsCurrent if i]
    #if len(optionsCurrent) < 1:
        #print('------------ LOG CURRENT SEARCH STRING IS EMPTY --------')

    optionsPrevious = dataPrevious['SEARCH_STRING'].split('--')
    # Remove any empty elements from the list
    optionsPrevious = [i for i in optionsPrevious if i]
    #if len(optionsPrevious) < 1:
        #print('------------ LOG PREVIOUS SEARCH STRING IS EMPTY --------')


    #print('-------->>optionsPrevious:')
    #pprint(optionsPrevious)
    #print('-------->>optionsCurrent:')
    #pprint(optionsCurrent)

    if list(set(optionsPrevious) - set(optionsCurrent)):
        print('iv_Logger: Recording OPTION REMOVAL')
        listDifference = list(set(optionsPrevious) - set(optionsCurrent))
        for oid in listDifference:
            grp = "befor loop"
            def1 ="befor loop"           
            try:
                optionObj = Option.objects.get(id=oid)
                grp = optionObj.groupName
                def1 = optionObj.definition
            except ObjectDoesNotExist:
                grp = ' which was not found in dB'
                def1 = ""
            finally:
                style_classes = ""
                classes.append("username removed-option")
                for styleclass in classes:
                    style_classes += styleclass + " "
                lineStr = '<span class="'+style_classes+'">'+user +'</span> <span class="removed-option"><span class="log-mode">'+logMode+'-</span><span class="log-action">removed</span> '+'<span class="option-id">('+oid+')</span>  <span class="option-title">'+ grp +'::'+def1+'</span>  <span class="timestamp">'+timeString+'</span></span>'
                print(lineStr)
                log_lines.append({ "log_id": log_id, "log":lineStr })
        
        return log_lines

    if list(set(optionsCurrent) - set(optionsPrevious)):
        print('iv_Logger: Recording OPTION ADDITION')
        listDifference = list(set(optionsCurrent) - set(optionsPrevious))
        listToStr = ' '.join(map(str, listDifference))
        for oid in listDifference:
            grp = "befor loop"
            def1 ="befor loop"           
            try:
                optionObj = Option.objects.get(id=oid)
                grp = optionObj.groupName
                def1 = optionObj.definition
            except ObjectDoesNotExist:
                grp = ' which was not found in dB'
                def1 = ""
            finally:
                style_classes = ""
                classes.append("username added-option")
                for styleclass in classes:
                    style_classes += styleclass + " "
                lineStr = '<span class="'+style_classes+'">'+user +'</span> <span class="added-option"><span class="log-mode">'+logMode+'-</span><span class="log-action">added</span> '+'<span class="option-id">('+oid+')</span> <span class="option-title">'+ grp +'::'+def1+'</span>  <span class="timestamp">'+timeString+'</span></span>'
                print(lineStr)
                log_lines.append({ "log_id": log_id, "log":lineStr })
        
        return log_lines
    
    """
       In this case, nothing was added by the user so no logs 
       should be entered. However, this allows for legacy logs
       & backward compatability logs, etc. to be added by the 
       API on the fly (when none prev exist).
    """
    if "API:" in user and "log_timestamp:" in logObj.data  :
        
        #print('======================= logObj.data =========================')
        #print(user)
        #pprint(logObj.data)

        # if ":bkwd cmpatbl updt" in user :
        #     logtype_style = "backward-compatibile"
        if "API:" in user :
            classes.append("api-added")
        if "legacy log" in user :
            classes.append("legacy-log")
        for oid in optionsCurrent:
            grp = "  "
            def1 =" - "           
            #print(str("OID:  "+oid))
            try:
                optionObj = Option.objects.get(id=oid)
                #print('optionObj')
                #pprint(optionObj)
                grp = optionObj.groupName
                def1 = optionObj.definition
            except ObjectDoesNotExist:
                grp = ' which was not found in dB'
                def1 = ""
            finally:
                style_classes = ""
                for styleclass in classes:
                    style_classes += styleclass + " "
                lineStr = '<span class="'+style_classes+'">'+user +'</span> <span class=""><span class="log-action">added</span> '+'<span class="option-id">('+oid+')</span> <span class="option-title">'+ grp +'::'+def1+'</span>  <span class="timestamp">'+timeString+'</span></span>'
                #print(lineStr)
                log_lines.append({ "log_id": log_id, "log":lineStr })
    
    return log_lines




"""
This create a log inthe the database of
    User, action, modelType and object properties.
Params:
    user: ste | a username or username associated with an API key or an API indicator
    action: str | "create", "update", "delete", <customized label>
    modelType: str | "Asset", "Option", "Category" ... etc
    objectInput: object | the object model to iterate its properties for the log   
"""
def commitLogEntryToDatabase(logged_user="", action="update", modelType ="", objectInput=False, mode="default", extraIn="" ):
    
    #print('commitLogEntryToDatabase OBJECT IN: ')
    #print('objectInput TYPE = '+str(type(objectInput)))
    #pprint(objectInput)
    extra_text = ""
    extraDict = {}
    filename = "empty"

    if isinstance(extraIn, str):
        extra_text = extraIn
        #pprint(extraIn)
    
    if isinstance(extraIn, dict):
        extraDict = extraIn

    if isinstance(objectInput, dict):
        key = 'fileName'
        if key in objectInput.keys():
            filename = objectInput['fileName']

    if isinstance(objectInput, (Asset,ivault_t_search,ivault_t_vals)):
        #print('objectInput TYPE = '+str(type(objectInput)))
        filename = objectInput.fileName

    if isinstance(objectInput, (Option,ivault_t_options)):
        if isinstance(extraIn, dict):
            filename = extraDict['fileName']

    #cleans filename
    filename = str(filename)
    filename = filename.replace("media/","").replace("/","")

    date = datetime.now(pytz.timezone('US/Central'))
    log_timestampString = ' log_timestamp:'+date.strftime("%Y-%m-%d %H:%M:%S")

    textData = build_log_text(action, modelType, objectInput) + " " +extra_text + ", " + log_timestampString
    textData = (textData[:1485] + '...TRUNCATED') if len(textData) > 1485 else textData

    #print('__iV_Logger__: '+ textData)
    # Set id to None when creating a new object
    id = None
    ivLogObj = IvaultLog(id, logged_user, filename, mode, textData)
    #print('Logger Just prior to save() ivLogObj.mode ')
    #pprint(ivLogObj.mode)
    ivLogObj.save()



"""
This build log text based on action and object
Params:
    action: str | "create", "update", "delete", <customized label>
    modelType: str | "Asset", "Option", "Category" ... etc
    objectInput: object | the object model to iterate its properties for the log
"""
def build_log_text(action="update", modelType ="", objectInput=False ):
    # DEV FEEDBACK
    #if 'BEFORE UPDATE' in action.upper():
    #    print('INSIDE: build_log_text()')
    #    print('action = '+ action.upper())
    #    print('modelType = '+ modelType)
    #    print('objectInput')
    #    pprint(objectInput)

    logtext = "---"
    logtext = action.upper()+" "+modelType+" | "

    if objectInput and isinstance(objectInput,(Asset,Option, ivault_t_search, ivault_t_options, ivault_t_vals,BatchTagHistory)) :
        for attr, value in objectInput.__dict__.items():
            if(attr != "_state"):
                logtext += attr.upper() +":"+str(value)+", "
    
    # DEV FEEDBACK
    # if 'BEFORE UPDATE' in action.upper():
    #     print('LOGTEXT:'+logtext)
    return logtext


"""
  This function first attempt the fastest way to lookup
  logs. If nothing found, it will try the slower method.

  Faster way:  queryLogByFilenameColumn(fn)
  Slower way:  queryLogByFilenameInDataColumn(fn)
  
  The Logger related funtion have been re-written so that 
  soon almost all the new logs  will be saved the faster way.

  An improvment would be to write a script to "retro-fit"
  the legacy logs for the faster way to query.
"""
def queryLogsByFilename(fn):
    ivaultLogData = queryLogByFilenameColumn(fn)
    #print('def queryLogsByFilename(fn) attempt 1')
    #pprint(ivaultLogData)
    # If unable to find logs the fast way then try the other way.
    if not ivaultLogData :
        ivaultLogData = queryLogByFilenameInDataColumn(fn)
        #print('def queryLogsByFilename(fn) attempt 2')
        #pprint(ivaultLogData)
    return ivaultLogData

def queryLogByFilenameColumn(fn):
    try:
        # fn.replace('/media/media/media/media/','/media/')
        queryDat = IvaultLog.objects.filter(filename=str(fn))
        #print("=== !FAST! LOG DATA ===")
        return queryDat
    except:
        return False

def queryLogByFilenameInDataColumn(fn):
    try:
        queryForFilename = Q() 
        # Use django's Q() to do an OR search filter for the filename
        # in different possible contexts
        # Possible fileName Context 01 
        queryForFilename  |= Q(data__contains="FILENAME:"+fn+",")
        # Possible fileName Context 02 
        queryForFilename  |= Q(data__contains=" "+fn+",")
        # Possible fileName Context 03 
        queryForFilename  |= Q(data__contains=" "+fn+" ")
        queryDat = IvaultLog.objects.filter(queryForFilename)
        #print("=== ~~SLOW~~ LOG DATA ===")
        return queryDat
    except:
        return False