from django.shortcuts import render
from django.views.generic import TemplateView
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.http import JsonResponse
from core.models import Asset, Option, ivault_t_search, ivault_t_options, ivault_t_vals
from core.serializers import AssetSerializer, OptionSerializer
from core.functions import create_core_ivault_t_search_and_vals, update_core_ivault_t_search_and_vals
from pprint import pprint
from .functions import create_thumb
import os
import uuid
import json
from .s3_uploader import upload_file_to_S3
from pathlib import Path
from django.http import StreamingHttpResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from iv_logger.functions import commitLogEntryToDatabase, build_log_text
from PIL import Image
Image.MAX_IMAGE_PIXELS = None

"""
This function handles the initial upload of files.
 - Saves them in a temporary folder
Prepares them for being process for:
  - Upload to S3 Bucket 
  - Associating tags and meta data to the image
   - Storing in the database
"""
@csrf_exempt
def api_initialUpload(request):
    context = {}
    preUploadData = []
    optionsData = []
    bucket = settings.S3_BUCKET
    bucketSubDir = settings.S3_BUCKET_SUB_DIR + "/"
    data = {}
    is_tiff = False
    allowTempFileSave = True

    print('REQUEST HEADERS')
    pprint(type(request.headers))
    pprint(request.headers)

    """
       Prevent bloating servers with tests
    """
    if 'TEST' in request.headers and 'loadtest' in (request.headers['TEST']).lower() :
        print('This ia a Load Test so allowTempFileSave = False')
        allowTempFileSave = False
        context['test_data'] = {}
        context['test_data']["type"] = "Load Test"
        context['test_data']["allowTempFileSave"] = str(allowTempFileSave)

    if request.method == 'POST' and 'multipart/form-data' in request.headers['Content-Type']:
        # Config var representing the files being uploaded
        upload_files = list(request.FILES.items())
        storage_location = settings.MEDIA_ROOT + '/temp'
        temp_img_dir = '/media/temp/'
        fs = FileSystemStorage(storage_location)

        for incr, singleFile in enumerate(upload_files):
            fileObj = singleFile[1]
            print('POST:api_preUpload['+str(incr)+']')
            print(singleFile)
            pprint(fileObj)
            print(fileObj.name)
            # Starts at 1 not 0 for human readable
            incr += 1
            assetDict={}
            preUploadUniqueId = uuid.uuid1();
            tempStoragePath = storage_location+'/'+fileObj.name
            print(tempStoragePath)
            #create_thumb(tempStoragePath, 80)

            file_name = Path(fileObj.name).name
            file_name = sanitizeFileName(file_name)
            #=====================================
            if(IsExistingFile(fileObj.name)):
                # Ask user: REPLACE EXISTING FILE?
                print(fileObj.name +' is an EXISTING FILE')
                optVals = GetExistingAssetOptionValues(fileObj.name)

                s_string = BuildAssetSearchString(optVals)
                #print('S_STRING: ' + s_string)
                assetDict['incr'] = incr
                assetDict['existing_asset'] = True
                #Create instance of this Asset (uploaded File)
                assetId = Asset.objects.only('id').get(fileName=file_name).id
                asset = Asset(id=assetId,fileName=fileObj.name, search_string=s_string)
                # Serialize so VueJs can process easily
                serializedAsset = AssetSerializer(asset)
                assetDict['human_readable_id'] = serializedAsset.data['id']
                assetDict['id'] = serializedAsset.data['id']
                assetDict['fileName'] = serializedAsset.data['fileName']
                assetDict['search_string'] = serializedAsset.data['search_string']
                assetDict['timestamp'] = serializedAsset.data['timestamp']
                assetDict['options'] = serializedAsset.data['options']
                assetDict['tempStoragePath'] = tempStoragePath
                assetDict['do_save_to_s3'] = True 
                assetDict['temp_img_dir'] = temp_img_dir
                # If .tiff replace with created thumbnail img
                if (tempStoragePath.lower().find('.tif') != -1):
                    is_tiff = True
                    assetDict['temp_img_path'] = temp_img_dir + file_name +'_thumb.png'
                else:
                    assetDict['temp_img_path'] = temp_img_dir + file_name 
                #assetDict['s3_ivault_uri'] = settings.S3_IVAULT_URI + file_name <-- for PROD may need to uncomment this
                # this url for DEV work
                assetDict['s3_ivault_uri'] = 'https://s3.amazonaws.com/'+bucket+'/'+bucketSubDir + file_name
                assetDict['uploaded'] = False
                assetDict['seq'] = incr

                preUploadData.append(assetDict)                  

            else:
                print(fileObj.name +' is NOT an EXISTING FILE')
                assetDict['existing_asset'] = False
                #Create instance of this Asset (uploaded File)
                assetId = 'Not existing'
                asset = Asset(id=preUploadUniqueId,fileName=file_name, search_string='')
                # Serialize so VueJs can process easily
                serializedAsset = AssetSerializer(asset)
                assetDict['human_readable_id'] = 'new'
                assetDict['id'] = serializedAsset.data['id']
                assetDict['fileName'] = serializedAsset.data['fileName']
                assetDict['search_string'] = serializedAsset.data['search_string']
                assetDict['timestamp'] = serializedAsset.data['timestamp']
                assetDict['options'] = serializedAsset.data['options'] 
                assetDict['tempStoragePath'] = tempStoragePath  
                assetDict['do_save_to_s3'] = True 
                assetDict['temp_img_dir'] = temp_img_dir 
                # If .tiff replace with created thumbnail img
                if (tempStoragePath.lower().find('.tif') != -1):
                    is_tiff = True
                    assetDict['temp_img_path'] = temp_img_dir + file_name +'_thumb.png'
                else:
                    assetDict['temp_img_path'] = temp_img_dir + file_name 
                assetDict['s3_ivault_uri'] = False
                assetDict['uploaded'] = False
                assetDict['seq'] = incr
                context['success'] = True 

                preUploadData.append(assetDict)
        
            # SAVES FILE TO TEMP FOLDER UNTIL READY
            
            if allowTempFileSave :
                print("SAVES FILE TO TEMP FOLDER UNTIL READY")
                unique_filename = fs.save(fileObj.name, fileObj)
                print('AFTER fs.save' + unique_filename)
                
                if is_tiff:
                    create_thumb(tempStoragePath, 500)
                    # Reset is_tiff
                    is_tiff = False

                context['url'] = fs.url(unique_filename)
                context['unique_filename'] = unique_filename

            context['allowTempFileSave'] = str(allowTempFileSave)
            context['success'] = True 


        # Options data is for the Options assignment SELECT element
        optionGroups = []
        optionsData = Option.objects.all().values('groupName').distinct().order_by('groupName')
        #serializedOptions = OptionSerializer(optionsData, many=True)
        
        for opt in optionsData:
            optionGroups.append(dict(groupName=opt['groupName']))

        context['preUploadData'] = preUploadData 
        context['selectOptionsGroups'] = optionGroups 

        static_asset_filesnames = {'javascript':'uploader.js', 'styles':'uploader.css', 'vuejs':'uploader_vue.js'}
        context['static_asset_filesnames'] = static_asset_filesnames
            
        context['status'] = 200
        return JsonResponse(context, safe=False)

    static_asset_filesnames = {'javascript':'uploader.js', 'styles':'uploader.css'}
    context['static_asset_filesnames'] = static_asset_filesnames
    context['success'] = False 
    return JsonResponse(context, status=400) 

@csrf_exempt
def api_process_asset_upload(request):
    
    # SET UP SECURITY TOKEN HERE
    # ===========================
    print('def api_process_asset_upload(request)')
    pprint(request.body)
   
    data = {}
    resp_msg = '<span class="warning">FAILED to uploaded!</span>'
    log_msg = 'dB not inserted or updated'
    logMode = 'default'
    uploaded = False
    success = False
    commited = False
    do_save_to_S3 = False
    bucket = settings.S3_BUCKET
    bucketSubDir = settings.S3_BUCKET_SUB_DIR + "/"
    img_src = 'not-calculated'
    listOfTempFiles=[]

    data['uploaded'] = uploaded
    data['commited'] = commited
    data['success'] = success 
    status_code = 500

    allowS3FileSave = True

    tokenKey = request.META.get('HTTP_AUTHORIZATION').replace("Token ", "")
    username_authenticatedByToken = Token.objects.get(key=tokenKey).user.username

    print('REQUEST HEADERS')
    pprint(request.headers)

    """
       Prevent bloating S3 Buckets with tests
    """
    if 'TEST' in request.headers and 'loadtest' in (request.headers['TEST']).lower() :
        print('This ia a Load Test so allowS3FileSave = False')
        allowS3FileSave = False
        data['test_data'] = {}
        data['test_data']["type"] = "Load Test"
        data['test_data']["allowS3FileSave"] = str(allowS3FileSave)

    try:
        post_body = request.body.decode('utf-8')
        upload = json.loads(post_body)

        if isinstance(upload, dict):
            if 'mode' in upload.keys():
                logMode = upload['mode']
            
        object_name = Path(upload['fileName']).name
        # Remove spaces
        object_name = object_name.replace(' ','_')
        s_string = BuildAssetSearchString(upload['options'])
    except:
        status_code = 200
        data['resp_msg'] = '<span class="warning">Payload is not in expected form.</span>'
        data['log_msg'] = 'dB not inserted or updated'
        return JsonResponse(data, status=status_code)         


    """
     CREATE ASSET OBJECT
    """
    if(IsExistingFile(object_name)):
        log_msg = 'UPDATING dB for '+object_name +' as an EXISTING ASSET'

        assetObject = Asset.objects.get(fileName=object_name)
        
        if ivault_t_search.objects.filter(fileName=object_name).exists() :
            ivaultTSearchObject = ivault_t_search.objects.get(fileName=object_name)
        else:
            ivaultTSearchObject = ivault_t_search(fileName=object_name)

        # reset (disassociate) options before adding the updated optios set
        assetObject.options.clear()
        # Set all the new options
        for opt in upload['options']:
            assetObject.options.add( Option.objects.get(id=int(opt['id'])))
            

        assetObject.search_string = s_string
        # This is for backward compatability with wellborn.com Curator
        ivaultTSearchObject.search_string = s_string
        ivaultTSearchObject.save()

        log_text_before_update = build_log_text("before updated", "Asset", assetObject)

        assetObject.save()
        commitLogEntryToDatabase(username_authenticatedByToken, "update by uploader", "Asset", assetObject, logMode, log_text_before_update)
        
        """
          For backwards compatability with wellborn.com Curator
        """
        serializedAsset = AssetSerializer(assetObject, many=False)
        update_core_ivault_t_search_and_vals(serializedAsset.data)

    else:
        log_msg = 'INSERTING INTO dB for '+object_name +' as a NEW ASSET'
        assetObject = Asset(fileName=object_name)
        assetObject.search_string = s_string
        assetObject.save()

        # Set all the new options
        for opt in upload['options']:
            OptionObj = Option.objects.get(id=int(opt['id']))
            assetObject.options.add(OptionObj)
            pseudoObject = {}
            pseudoObject['fileName'] = object_name            
            commitLogEntryToDatabase(username_authenticatedByToken, "create/upload", "Option", OptionObj, logMode, pseudoObject)

        assetObject.save()
        commitLogEntryToDatabase(username_authenticatedByToken, "create/upload", "Asset", assetObject, logMode)

        """
          For backwards compatability with wellborn.com Curator
        """
        serializedAsset = AssetSerializer(assetObject, many=False)
        create_core_ivault_t_search_and_vals(serializedAsset.data)        


    """
    ////////////////////////////////////
     S3 UPLOAD
    ////////////////////////////////////
    """
    # Extra arguments for S3 Processing
    extraArgs = {'ACL': 'public-read', 'ContentType': 'image'}
    # Send her up!
    try:
        mediaUplaodFolder = '/media/'
        uploadedfilename = upload['fileName'].replace(' ','_')
        filename = uploadedfilename.replace(mediaUplaodFolder, '')
        filenameFragments = filename.split(".")
        uploadedFileSuffix = filenameFragments[len(filenameFragments)-1]
        uploadedTempImageFileLocation = upload['tempStoragePath']
        tempImageFileLocationCleansed = uploadedTempImageFileLocation.replace(' ','_')
        tempImageFolder = tempImageFileLocationCleansed.replace(filename, '')
        listOfTempFiles.append(tempImageFileLocationCleansed)
        #print('====Try upload_file_to_S3 SOON======')
        #print('uploadedFileSuffix: '+uploadedFileSuffix)
        #print('tempImageFolder: '+tempImageFolder)
        #print('filename: '+filename)
        print('about to create pillow image object')
        pillowImageObj = Image.open(uploadedTempImageFileLocation)
        pprint(pillowImageObj)
        print('about to save pillow image object as '+"cleansed_"+tempImageFileLocationCleansed)
        #pillowImageObj.save("cleansed_"+tempImageFileLocationCleansed)
        img_src = 'https://s3.amazonaws.com/'+bucket+"/"+bucketSubDir+filename
        # Case insensitive check for tif, tiff, TIF, TIFF, tiF ...
        if 'tif' in uploadedFileSuffix.lower():
            #//////////////////
            # After examining the legacy iVault code I have determined the following.
            # In the case of a TFF file being uploaded:
            # 
            # -  A copy of the original TIFF file is uploaded (full size) to S3 but is not displayed in search results.
            # -  A copy of the tiff file is created with the largest dimension being 500px and converted to a png file.
            #    -  The PNG copy is what is displayed in search results.
            #    -  The name of the .png file follows the naming convention: <original filename>.tif_thumb.png
            #  patter = filename.tif_thumb.png
            #//////////////////
            # Max pixels for width or height
            largeSideMax = 500
            #create_thumb(uploadedfilename, largeSideMax)
            # Get the size dims of the tiff
            width, height = pillowImageObj.size
            #print('=== WD --->:', width)
            #print('=== HT --->:', height)
            # Determine which size is bigest & calc ratio
            if width > height:
                sizingRatio = largeSideMax/width
            else:
                sizingRatio = largeSideMax/height
            #Apply that ratio to both sides
            resizedWidth = width * sizingRatio
            resizedHeight = height * sizingRatio
            reNameToPng = filename + "_thumb.png"
            reNamedImagePathPng = tempImageFolder+reNameToPng
            listOfTempFiles.append(reNamedImagePathPng)
            
            img_src = 'https://s3.amazonaws.com/'+bucket+"/"+bucketSubDir+reNameToPng
            #print('filename : '+filename)
            #print('temp location: '+reNamedImagePathPng)
            #print('S3 flder/filename: '+bucketSubDir+reNameToPng )
            rgb_image = pillowImageObj.convert('RGB')
            resized_image = rgb_image.resize((round(resizedWidth),round(resizedHeight)))
            resized_image.save(reNamedImagePathPng, 'PNG')
            
            if allowS3FileSave :
                # Store the png representation of the TIFF
                try:
                    print('Attempting Thumnail upload for tiff')
                    print('reNamedImagePathPng: '+reNamedImagePathPng)
                    print('bucketSubDir+reName: '+bucketSubDir+reNameToPng)
                    S3UploadResult = upload_file_to_S3(tempImageFolder+reNameToPng, bucket, bucketSubDir+reNameToPng, extraArgs)
                except:
                    data['success'] = False
                    data['commited'] = False
                    data['uploaded'] = False
                    data['resp_msg'] = '<span class="warning">FAILED THUMBNAIL UPLOAD to upload asset to S3! Check the media path is valid.</span>'          
                    data['log_msg'] = log_msg
                    status_code = 500   
                    return JsonResponse(data, status=status_code) 

        if allowS3FileSave:    
            # Store the original File
            print('upload_file_to_S3()')
            S3UploadResult = upload_file_to_S3(upload['tempStoragePath'], bucket, bucketSubDir+filename, extraArgs)
            #print('==== S3UploadResult ====>')
            #pprint(S3UploadResult)

    except:
        data['success'] = False
        data['img_src'] = img_src
        data['filename'] = filename
        data['type'] = uploadedFileSuffix
        data['commited'] = False
        data['uploaded'] = False
        data['resp_msg'] = '<span class="warning">FAILED to upload asset to S3! Check the media path is valid.</span>'          
        data['log_msg'] = log_msg
        status_code = 500   
        return JsonResponse(data, status=status_code)       

    if(S3UploadResult):
        # Create a log entry of the upload and associated Options
        print('===>  Asset  OBJECT  ===')
        pprint(object_name)

        action="create"
        modelType ='S3 upload'
        logText = 'Sucesfully uploaded ' + object_name + ' to S3!'
        pseudoObject = {}
        pseudoObject['fileName'] = object_name
        commitLogEntryToDatabase(username_authenticatedByToken, action, modelType, pseudoObject, logMode, logText )

        resp_msg = 'Sucesfully uploaded to S3!'
        uploaded = True
        success = True
        status_code = 200
    
    else:
        # Create a log entry of the upload and associated Options
        print("S3 upload failed")
        action="create"
        modelType ='S3 upload'
        logText = 'S3 Upload -*- FAILED -*- for ' + object_name + '!'
        pseudoObject = {}
        pseudoObject['fileName'] = object_name
        commitLogEntryToDatabase(username_authenticatedByToken, action, modelType, pseudoObject, logMode, logText )

    """
    ////////////////////////////////////
     Delete the Temp upload file
    ////////////////////////////////////
    """ 
    if(S3UploadResult):
        for tempFl in listOfTempFiles:
            # Remove the upload from temp file path
            print("\n ===> Looking to remove "+tempFl)
            if os.path.exists(tempFl):
                try:
                    os.remove(tempFl)
                    print(' == REMOVED ==> '+ tempFl )
                    commited = True
                    status_code = 200
                except:
                    data['success'] = False
                    data['commited'] = False
                    data['uploaded'] = False
                    data['resp_msg'] = '<span class="warning">FAILED to remove the upload from temp file path! '+upload['tempStoragePath']+' does not exist</span>'          
                    data['log_msg'] = log_msg
                    status_code = 500
                    return JsonResponse(data, status=status_code)

            if os.path.exists(tempFl+"_thumb.png"):
                try:
                    os.remove(tempFl+"_thumb.png")
                    print(' == REMOVED ==> '+ tempFl+"_thumb.png" )
                    commited = True
                    status_code = 200
                except:
                    data['success'] = False
                    data['commited'] = False
                    data['uploaded'] = False
                    data['resp_msg'] = '<span class="warning">FAILED to remove the upload from temp file path! '+upload['tempStoragePath']+' does not exist</span>'          
                    data['log_msg'] = log_msg
                    status_code = 500
                    return JsonResponse(data, status=status_code)



    """
       Serialize so VueJs can process easily
    """
    serializedAsset = AssetSerializer(assetObject)
    print('serializedAsset OPTIONS')
    optionsOrderedDict = serializedAsset.data['options']
    pprint(serializedAsset.data['options'])
    
    optionsList = []
    # Convert ordered dicts to normal dict
    for orderedDictOption in serializedAsset.data['options']:
        optionsList.append(dict(orderedDictOption))

    data['resp_msg'] = resp_msg 
    data['id'] = serializedAsset.data['id']
    data['fileName'] = filename
    data['img_src'] = img_src
    data['search_string'] = serializedAsset.data['search_string']
    data['timestamp'] = serializedAsset.data['timestamp']
    data['options'] =  optionsList
    data['s3_ivault_uri'] = 'https://s3.amazonaws.com/'+bucket+'/'+bucketSubDir+object_name 
    data['uploaded'] = uploaded
    data['commited'] = commited
    data['success'] = success 
    data['log_msg'] = log_msg   

    print('DATA: ')
    pprint(data)
    return JsonResponse(data, status=status_code) 

@csrf_exempt
def api_upload_single_file_to_s3(request):
    context = {}
    logMode="default"
    preUploadData = []
    optionsData = []
    bucket = settings.S3_BUCKET
    bucketSubDir = settings.S3_BUCKET_SUB_DIR + "/"
    data = {}
    resp_msg = "Failed"
    success = False
    uploaded = False


    print('===== api_upload_single_file_to_s3 =====')
    if request.method == 'POST':
        is_tiff = False
        # Config var representing the file being uploaded
        upload_files = list(request.FILES.items())
        storage_location = settings.MEDIA_ROOT + '/temp'
        temp_img_dir = '/media/temp/'
        fs = FileSystemStorage(storage_location)
        fileTuple = upload_files[0]
        fileObj = fileTuple[1]
        print(type(fileObj))
        pprint(fileObj.name)
        s3_object_name = Path(fileObj.name).name
        print(type(s3_object_name))
        pprint(s3_object_name)
        s3_object_name = sanitizeFileName(s3_object_name)

        aid = request.POST['asset_id'];

        # SAVES FILE TO TEMP FOLDER UNTIL READY
        unique_filename = fs.save(fileObj.name, fileObj)
        tempStoragePath = storage_location+'/'+unique_filename

        if (tempStoragePath.lower().find('.tif') != -1):
           is_tiff = True
           #assetDict['temp_img_path'] = temp_img_dir + file_name +'_thumb.png'


        if is_tiff:
            create_thumb(tempStoragePath, 500)
            # reset is_tiff
            is_tiff = False

        """
         S3 UPLOAD
        """
        # Extra arguments needed for S3 Processing
        extraArgs = {'ACL': 'public-read', 'ContentType': 'image'}      
        # Send her up!
        S3UploadResult = upload_file_to_S3(tempStoragePath, bucket, bucketSubDir+s3_object_name, extraArgs)
    
        if(S3UploadResult):

            success  = True
            resp_msg = 'Sucesfully uploaded ' + s3_object_name + '!'
            uploaded = True

            # Remove the upload from temp file path
            if os.path.exists(tempStoragePath):
                os.remove(tempStoragePath)
                print('REMOVED '+ s3_object_name + ' from '+ tempStoragePath)

            # For tif file, Remove the upload from temp file path
            if os.path.exists(tempStoragePath+"_thumb.png"):
                os.remove(tempStoragePath+"_thumb.png")
                print('REMOVED '+ s3_object_name + ' from '+ tempStoragePath+"_thumb.png")

        else:
            resp_msg = '<span class="warning">FAILED to uploaded'+s3_object_name+'!</span>'

        AssetObj = Asset.objects.get(id=aid)
        AssetObj.fileName = s3_object_name;
        AssetObj.save();
        serializedAsset = AssetSerializer(AssetObj)
        data['id'] = serializedAsset.data['id']
        data['fileName'] = serializedAsset.data['fileName']
        data['search_string'] = serializedAsset.data['search_string']
        data['timestamp'] = serializedAsset.data['timestamp']
        data['options'] = serializedAsset.data['options'] 
        data['s3_ivault_uri'] = 'https://s3.amazonaws.com/'+bucket+'/'+bucketSubDir+s3_object_name 

    data['resp_msg'] = resp_msg 
    data['success']  = success
    data['uploaded'] = uploaded

    return JsonResponse(data) 



#  /////////////////////////////////

def ajax_delete_upload_temp_files(request):
    """
    ////////////////////////////////////
     Delete the Temp upload file
    ////////////////////////////////////
    """
    storage_location = settings.MEDIA_ROOT + '/temp'
    #fs = FileSystemStorage(storage_location)
    post_body = request.body.decode('utf-8')
    print('STORAGE LOCATION:' + storage_location)
    print('POST:')
    pprint(post_body)
    
    payload = json.loads(post_body)
    data = payload
    data['path'] = storage_location
    data['files'] = []
    print('PAYLOAD:')
    print(data)
    incr = 0

    # Remove the upload from temp file path
    for filename in os.listdir(storage_location):
        file_path = os.path.join(storage_location, filename)

        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
                print('REMOVED '+ filename + ' from '+storage_location)
                msg = 'REMOVED: '+ filename + ' from ' + storage_location

            else: data['incr'] = {'msg':'Not a file'}
            error = False

        except Exception as e:
            error = 'Failed to delete %s. Reason: %s' % (file_path, e)
            print('ERR: ' + error)

        fileDat = {'filename': filename, 'msg': msg, 'err': error, 'path': file_path }
        data['files'].append(fileDat)

    #if os.path.exists(upload['tempStoragePath']):
    #    os.remove(upload['tempStoragePath'])
    #    print('REMOVED '+ object_name + ' from '+ upload['tempStoragePath'])
    #return payload
    return JsonResponse(data, safe=False) 

def api_definitions_by_option_group(request):
    data = []
    optionGroupName = request.GET['optionGroupName']
    options  = Option.objects.filter(groupName=optionGroupName).order_by('definition')
   
    for dat in options:
        # Make a list of dictionaries to be converted to JSON
        # safe=False must be set for JsonResponse(data, safe=False) to work 
        # with a list of dictionaries
        data.append({'id':dat.id,'groupName': dat.groupName, 'definition':dat.definition})

    return JsonResponse(data, safe=False) 

# Add object to a many to many field            
#   eg. -->  Asset.options.add(Option.objects.get(id=definition_id))

def ajax_add_option_val_to_asset(request):
    data = {}
    asset_id = request.GET['assetId']
    definition_id = request.GET['assetOptionId']
    assetObject = Asset.objects.get(pk=asset_id)
    #pprint(assetObject)
    assetObject.options.add(Option.objects.get(pk=definition_id))
    assetOptions = Option.objects.filter(asset=asset_id).order_by('groupName')
    #Create data that can be seriralized into JSON
    for dat in assetOptions:
        # Use groupName as key so it sorts on groupName
        # Concoatination is needed to prevent the array
        # from ovverwritting its own values
        data[dat.groupName+"_"+dat.definition] = {'id':dat.id,'groupName': dat.groupName, 'definition':dat.definition}

    # return the options data for the specified asset
    return JsonResponse(data)

def ajax_remove_option_val_to_asset(request):
    data = {}
    asset_id = request.GET['assetId']
    definition_id = request.GET['assetOptionId']
    assetObject = Asset.objects.get(pk=asset_id)
    pprint(assetObject)
    assetObject.options.remove(Option.objects.get(pk=definition_id))
    assetOptions = Option.objects.filter(asset=asset_id).order_by('groupName')
    #Create data that can be seriralized into JSON
    for dat in assetOptions:
        # Use groupName as key so it sorts on groupName
        data[dat.groupName+"_"+dat.definition] = {'id':dat.id,'groupName': dat.groupName, 'definition':dat.definition}

    # return the options data for the specified asset
    return JsonResponse(data)

 
@csrf_exempt
def api_removeUploadedTempFiles(request):
    data = {}
    data['success'] = False
    data['errors'] = []
    data['removed_files'] = []
    preThumbnailTiffs = []
    removedFilesStr = ''

    if request.method == 'POST':
        payload = request.body.decode('utf-8')
        jsonRemoveTheseFiles = json.loads(payload)
        #print('---- jsonRemoveTheseFiles ----')
        #pprint(jsonRemoveTheseFiles)
        data['removeTheseFiles'] = jsonRemoveTheseFiles
        # Config var representing the files being uploaded
        storage_location = settings.MEDIA_ROOT + '/temp'
        temp_img_dir = '/media/temp/'
        fs = FileSystemStorage(storage_location)
        data['storage_location'] = storage_location
        
        # Include tiff that thumbnail was made from (pre-thumbnail tiff)
        for filename in jsonRemoveTheseFiles:
            if (filename.lower().find('.tif') != -1):
                preThumbnailTiffs.append(filename.replace('_thumb.png',''))
        
        # Add the pre-thumbnail tiff files to the list
        jsonRemoveTheseFiles = jsonRemoveTheseFiles + preThumbnailTiffs

        # Remove the files
        for filename in jsonRemoveTheseFiles:
            # Cleanup filename prevent dupe '/media/temp/'
            filename = filename.replace('/media/temp/', '')
            # Configure file location
            removePath = storage_location + '/' + filename
            
            try:
                os.unlink(removePath)
                data['success'] = True
                data['removed_files'].append(removePath)
                removedFilesStr += removePath + ", "
                
                print('Files removed: ' + removePath)

            except Exception as e:
                error = 'Failed to delete %s. Reason: %s' % (removePath, e)
                print('ERR: ' + error)
                data['errors'].append(error)
                
    # return the options data for the specified asset
    if data['success']:
        data['resp_msg'] = "removed files: " + removedFilesStr
    return JsonResponse(data)        


def IsExistingFile(fileName):
    return Asset.objects.filter(fileName=fileName).count()

def GetExistingAssetOptionValues(fileName, serializeResults=False):
    ass_id = Asset.objects.only('id').get(fileName=fileName).id
    pprint(ass_id)
    options = Option.objects.filter(asset=ass_id).order_by('groupName')
    if serializeResults:
        # Serialize so VueJs can process easily
        serializedOptions = OptionSerializer(options, many=True)
        return  serializedOptions.data
    return options 

def BuildAssetSearchString(optVals):
    s_string = "--"
    for Opt in optVals:
        pprint(Opt)
        if isinstance(Opt, dict):
            s_string = s_string + str(Opt['id']) + "--"
        else:
            s_string = s_string + str(Opt.id) + "--"
        
    return s_string 

def sanitizeFileName(str, delim='_'):
    print('sanitizeFileName IN: ' + str)
    # Get rid of bad chars like psace etc.
    bad_chars_list = [' ', '%20']
    string_out = str
    for itm in bad_chars_list:
      string_out = string_out.replace(itm, delim)
    print('sanitizeFileName OUT: ' + string_out)
    return string_out


def LoadAssetIntoDatabase(assetObj):
    # SaveAssetOptionValues(assetObj)
    # Process/ReProcess Search String into assetObj
    pass

def SaveAssetOptionValues(assetObj):
    if request.method == 'POST':
        # Get the option values
        # Add/Delete the option values to assetObj
        pass

def ProcessSearchStringIntoAsset(assetObj):
    pass

def UserImplimentsTagBot(x):
    pass





