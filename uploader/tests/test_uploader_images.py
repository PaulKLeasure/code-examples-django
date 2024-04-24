from rest_framework.test import APIRequestFactory, APITestCase
from django.conf import settings
from uploader.views_api import api_initialUpload
from iv_logger.models import IvaultLog 
from pprint import pprint
import json
from io import BytesIO
from PIL import Image 
import pytest
import os, sys, stat
    

"""
 Useing Django's SimpleUploadedFile in combination
 with Pytest to test actual upload handling
 
"""
from django.core.files.uploadedfile import SimpleUploadedFile
@pytest.mark.urls('uploader.urls_api')
@pytest.mark.django_db
@pytest.mark.order(1)
def test_api_upload_assets(client):
	file = SimpleUploadedFile(
        "../../../test_assets/UnitTest_upload_image.png", 
        b"intentionly nothing", 
        content_type="image/png"
        )
	payload = {"upload_files": [file]}
	resp = client.post("/upload-assets/", payload, format="multipart")
	data = json.loads(resp.content)
	#print('TEST DATA')
	#pprint(data)
	assert resp.status_code == 202
	assert  isinstance(data['success'], bool)
	assert  isinstance(data['preUploadData'][0]['id'], int)
	assert  isinstance(data['preUploadData'][0]['seq'], int)
	assert  isinstance(data['preUploadData'][0]['options'], list)
	assert  isinstance(data['preUploadData'][0]['fileName'], str)
	assert  isinstance(data['preUploadData'][0]['tempStoragePath'], str)
	# If you do more calls in this method with the same file then seek to zero
	file.seek(0)


"""
 Test the processing of data associated with an 
 upload. becasue the process relies on variables
 That django creates this must be an "actual" uploaded 
 file as opposed to an "in memory" upload
 NOTE: This test DEPENDS on test_api_upload_assets
       to RUN FIRST which uploads the file:
       ../../test_assets/UnitTest_upload_image.png.
       At the end of this test, the uploaded test
       file is deleted by the app function:
       api_process_asset_upload.
 CLEANUP:
       - As stated above the uploaded file is removed from media/temp dir
       - The file is nOT removed from S3 since is is always the same name'
         and therefore not multiplying
 TEST VARIATIONS:
       This test has been run with the payload in various broken states
       to ensure that it properly fails. The variouse broken state are
       numerous and have not been included in the Unit Testing code in 
       order to keep the code base and time it takes to run test reasonable.
"""
#from django.core.files.uploadedfile import SimpleUploadedFile
@pytest.mark.urls('uploader.urls_api')
@pytest.mark.django_db
@pytest.mark.order(2)
def test_api_commit_batch(client):
    payload_dict = {"do_save_to_s3": True,
                    "existing_asset": False,
                    "fileName": "/media/UnitTest_upload_image.png",
                    "human_readable_id": "new",
                    "id": 4.35973418451127e+37,
                    "options": [{"definition": "Active",
                                 "groupName": "General",
                                 "id": 1021,
                                 "isBatch": 0},
                                {"definition": "CGI",
                                 "groupName": "General",
                                 "id": 3057,
                                 "isBatch": 0},
                                {"definition": "Public",
                                 "groupName": "General",
                                 "id": 1275,
                                 "isBatch": 0}],
                    "s3_ivault_uri": False,
                    "search_string": "",
                    "seq": 1,
                    "tempStoragePath": "/Users/pkleasure/Wellborn/Projects/django/ivault/iVault2/media/temp/UnitTest_upload_image.png",
                    "temp_img_dir": "/media/temp/",
                    "temp_img_path": "BAD__PATH/media/temp/UnitTest_upload_image.png",
                    "timestamp": "2021-06-30T16:56:35.222063Z",
                    "uploaded": False}
    resp = client.post("/commit-batch/", json.dumps(payload_dict), content_type="application/json")
    data = json.loads(resp.content)
    latest_id = IvaultLog.objects.latest('id').id
    log = IvaultLog.objects.get(id=int(latest_id) )
    print('==== FETCHED TEST LOG DATA=====')
    pprint(log.data)
    #print('TEST DATA')
    #pprint(data)
    assert resp.status_code == 200
    assert data['success'] == True
    assert data['commited'] == True
    assert data['uploaded'] == True
    assert  isinstance(data['success'], bool)
    assert  isinstance(data['resp_msg'], str)
    assert  isinstance(data['commited'], bool)
    assert  isinstance(data['uploaded'], bool)
    assert  isinstance(data['id'], int)
    assert  isinstance(data['options'], list)
    assert  isinstance(data['fileName'], str)
    assert  isinstance(data['search_string'], str)
    assert  isinstance(data['s3_ivault_uri'], str)   
    # Check that it gets logged
    assert  'UnitTest_upload_image.png, SEARCH_STRING:--1021--3057--1275--' in log.data
    assert  'UPDATE BY UPLOADER Asset' in log.data

"""
   Use io.BytesIO  and  PIL.Image to 
   create In Memory test images for testing 
   different kinds of image uplaods

   param dict as {'x':50,'y':100, 'type':'jpg'}
"""
def create_test_image(dict_in):
        #pprint(dict_in)
        file = BytesIO()
        image = Image.new('RGB', size=(dict_in['x'],dict_in['y']), color=(155, 0, 0)) 
        f_type = dict_in['type']
        name = 'test.' + f_type
        image.save(file, f_type)
        file.name = name
        file.seek(0)
        return file

"""
Use Django's RequestFactory in combination with
pytest-django to test in-memory simulated uploads
of multiple image types.

eg.
 img_params = {'mode':'RGB', 'x':50,'y':100, 'type':'png'}

"""
from django.test.client import RequestFactory
reqfact = RequestFactory()

def load_api_initialUpload_png_test(img_params):
    theFile = create_test_image(img_params).read()
    req=reqfact.post('api/uploader/upload-assets/',{"upload_files":[theFile]}, format='multipart')
    response = api_initialUpload(req)
    #print('--- IMAGE UPLOADED DATA ---')
    data = json.loads(response.content)
    #pprint(data)
    
    """
      Success with non commital acceptance for further processing
      This is becasue the upload configurator uploads temp files
      while the user configures tags for final upload. 
    """
    assert response.status_code == 202 

"""
=========================
PNG SM
=========================
"""
@pytest.mark.urls('uploader.urls_api')
@pytest.mark.django_db
def test_api_initialUpload_png(client):
    theFile = create_test_image({'mode':'RGB', 'x':25,'y':25, 'type':'png'}).read()
    payload = {"upload_files": [theFile]}
    response = client.post("/upload-assets/", payload, format="multipart")
    #print('--- IMAGE UPLOADED DATA ---')
    data = json.loads(response.content)
    #pprint(data)
    """
      Success with non commital acceptance for further processing
      This is becasue the upload configurator uploads temp files
      while the user configures tags for final upload. 
    """
    assert response.status_code == 202 


"""
==========================
 JPG SM
==========================
"""
@pytest.mark.django_db
def test_api_initialUpload_jpg():
    load_api_initialUpload_png_test({'mode':'LAB', 'x':50,'y':100, 'type':'png'})

"""
==========================
 TIFF SM
==========================
"""
@pytest.mark.django_db
def test_api_initialUpload_tif():
    load_api_initialUpload_png_test({'mode':'RGB', 'x':50,'y':100, 'type':'tiff'})

"""
==========================
 TIFF LARGE
==========================
"""
@pytest.mark.django_db
def test_api_initialUpload_tif_large():
    prevMaxMemory = settings.DATA_UPLOAD_MAX_MEMORY_SIZE
    #print("PREV DATA_UPLOAD_MAX_MEMORY_SIZE: "+str(prevMaxMemory))
    settings.DATA_UPLOAD_MAX_MEMORY_SIZE = 50000000
    #print("INCREASED DATA_UPLOAD_MAX_MEMORY_SIZE: "+str(settings.DATA_UPLOAD_MAX_MEMORY_SIZE))
    load_api_initialUpload_png_test({'mode':'RGB', 'x':3000,'y':3000, 'type':'tiff'})
    settings.DATA_UPLOAD_MAX_MEMORY_SIZE = prevMaxMemory
    #print("RESET BACK TO DATA_UPLOAD_MAX_MEMORY_SIZE: "+str(prevMaxMemory))

















