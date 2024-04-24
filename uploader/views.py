from django.shortcuts import render
from django.views.generic import TemplateView
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.http import JsonResponse
from core.models import Asset, Option
from core.serializers import AssetSerializer, OptionSerializer
from pprint import pprint
import os
import uuid
import json
from .s3_uploader import upload_file_to_S3
from pathlib import Path
from django.http import StreamingHttpResponse, HttpResponse


def upload(request):
    context = {}
    preUploadData = []
    optionsData = []
    bucketSubDir = settings.S3_BUCKET_SUB_DIR
    bucket = settings.S3_BUCKET
    #static_asset_filesnames = {'javascript':'uploader.js', 'styles':'uploader.css'}
    #context = {'static_asset_filesnames' : static_asset_filesnames}

    if request.method == 'POST':
        # Config var representing the files being uploaded
        upload_files = request.FILES.getlist('upload_files')
        
        # Djang native file storage handling class
        # storage_location = '/Applications/XAMPP/xamppfiles/htdocs/django/iv2/src/iVault2/temp'
        storage_location = settings.MEDIA_ROOT + '/temp'
        temp_img_dir = '/media/temp/'
        fs = FileSystemStorage(storage_location)

        pprint(request.POST)

        for incr, singleFile in enumerate(upload_files):
            print('POST:upload_files')
            print(singleFile.name)
            # Starts at 1 not 0 for human readable
            incr += 1
            assetDict={}
            preUploadUniqueId = uuid.uuid1();
            tempStoragePath = storage_location+'/'+singleFile.name
            print('TEMP STORAGE: ',tempStoragePath)

            file_name = Path(singleFile.name).name
            file_name = sanitizeFileName(file_name)
            #=====================================
            if(IsExistingFile(singleFile.name)):
                # Ask user: REPLACE EXISTING FILE?
                print('EXISTING  BUSTED!!')
                
                optVals = GetExistingAssetOptionValues(singleFile.name)
                for optval in optVals:
                    pprint(optval)

                s_string = BuildAssetSearchString(optVals)
                print('S_STRING: ' + s_string)
                assetDict['incr'] = incr
                assetDict['existing_asset'] = True
                #Create instance of this Asset (uploaded File)
                assetId = Asset.objects.only('id').get(fileName=file_name).id
                asset = Asset(id=assetId,fileName=singleFile.name, search_string=s_string)
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
                assetDict['temp_img_path'] = temp_img_dir + file_name 
                #assetDict['s3_ivault_uri'] = settings.S3_IVAULT_URI + file_name <-- for PROD may need to uncomment this
                # this url for DEV work
                assetDict['s3_ivault_uri'] = 'https://s3.amazonaws.com/'+bucket+'/'+bucketSubDir + file_name
                assetDict['uploaded'] = False

                preUploadData.append(assetDict)                  

            else:
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
                assetDict['temp_img_path'] = temp_img_dir + file_name
                assetDict['s3_ivault_uri'] = False
                assetDict['uploaded'] = False
                preUploadData.append(assetDict)
        

            unique_filename = fs.save(singleFile.name, singleFile)
    
            context['url'] = fs.url(unique_filename)
            context['unique_filename'] = unique_filename

        # Options data is for the Options assignment SELECT element
        optionGroups = []
        optionsData = Option.objects.all().values('groupName').distinct().order_by('groupName')
        #serializedOptions = OptionSerializer(optionsData, many=True)
        for opt in optionsData:
            optionGroups.append(dict(groupName=opt['groupName']))
        print('OPTIONS DATA')
        pprint(optionGroups) 
        #print('OPTIONS DATAserializedOptions')
        #pprint(serializedOptions.data) 
    
    
        #print('PRE UPLOAD DATA')
        #pprint(preUploadData) 
        context['preUploadData'] = preUploadData 
        context['selectOptionsGroups'] = optionGroups 

        static_asset_filesnames = {'javascript':'uploader.js', 'styles':'uploader.css', 'vuejs':'uploader_vue.js'}
        context['static_asset_filesnames'] = static_asset_filesnames
            
        return render(request, 'upload/confirm-upload.html', context)

    static_asset_filesnames = {'javascript':'uploader.js', 'styles':'uploader.css'}
    context['static_asset_filesnames'] = static_asset_filesnames

    return render(request, 'upload/upload.html', context)


def ajax_commit_file_asset_uploads(request):

    print('ajax_commit_file_asset_uploads')
    pprint(request)
    data = {}

    do_save_to_S3 = False

    post_body = request.body.decode('utf-8')
    upload = json.loads(post_body)

    bucketSubDir = settings.S3_BUCKET_SUB_DIR
    bucket = settings.S3_BUCKET

    print('PARSED JSON : upload')
    pprint(upload)
    
    object_name = Path(upload['fileName']).name
    s_string = BuildAssetSearchString(upload['options'])
    print('SEARCH_STRING: '+s_string)
    upload_process_complete = False

    """
     CREATE ASSET OBJECT
    """
    if(IsExistingFile(object_name)):
        print('ASSET EXISTING')
        assetObject = Asset.objects.get(fileName=object_name)
        # reset (disassociate) options before adding the updated optios set
        assetObject.options.clear()
        # Set all the new options
        for opt in upload['options']:
            assetObject.options.add( Option.objects.get(id=int(opt['id'])))
        assetObject.search_string = s_string
        assetObject.save()
        #if not do_save_to_S3:
        #    upload_process_complete = True
        
        pprint(assetObject)
    else:
        print('ASSET NEW')
        assetObject = Asset(fileName=object_name)
        assetObject.save()
        print('upload[options]')
        pprint(upload['options'])
        # Set all the new options
        for opt in upload['options']:
            assetObject.options.add( Option.objects.get(id=int(opt['id'])))
        assetObject.search_string = s_string
        assetObject.save()
        #if not do_save_to_S3:
        #    upload_process_complete = True
        pprint(assetObject)

    """
    ////////////////////////////////////
     S3 UPLOAD
    ////////////////////////////////////
    """
    # Extra arguments for S3 Processing
    extraArgs = {'ACL': 'public-read', 'ContentType': 'image'}
    # Send her up!
    S3UploadResult = upload_file_to_S3(upload['tempStoragePath'], bucket, bucketSubDir+object_name, extraArgs)

    if(S3UploadResult):
        resp_msg = 'Sucesfully uploaded!'
        uploaded = True
    else:
        resp_msg = '<span class="warning">FAILED to uploaded!</span>'
        uploaded = False

    """
    ////////////////////////////////////
     Delete the Temp upload file
    ////////////////////////////////////
    """ 
    if(S3UploadResult | upload_process_complete):
        # Remove the upload from temp file path
        if os.path.exists(upload['tempStoragePath']):
            os.remove(upload['tempStoragePath'])
            print('REMOVED '+ object_name + ' from '+ upload['tempStoragePath'])
    """
       Serialize so VueJs can process easily
    """
    serializedAsset = AssetSerializer(assetObject)
    data['resp_msg'] = resp_msg 
    data['id'] = serializedAsset.data['id']
    data['fileName'] = serializedAsset.data['fileName']
    data['search_string'] = serializedAsset.data['search_string']
    data['timestamp'] = serializedAsset.data['timestamp']
    data['options'] = serializedAsset.data['options'] 
    data['s3_ivault_uri'] = 'https://s3.amazonaws.com/'+bucket+'/'+bucketSubDir+object_name 
    data['uploaded'] = uploaded
    data['commited'] = True

    print('DATA: ')
    pprint(data)
    return JsonResponse(data) 

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

def ajax_option_group_values(request):
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





