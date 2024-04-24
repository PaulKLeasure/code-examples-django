from django.http import HttpRequest, HttpResponse, JsonResponse
from core import settings
from pprint import pprint
import json
import pytest
import inspect

"""
==========================================
 NOTES
==========================================
- TEST DATABASE: A test database is used. It
  helps in testing the API Tokens etc.
  See: 
  - @pytest.fixture(scope='session')
    def django_db_setup():
        ...
  - Also, @pytest.mark.django_db tells each
    test the database is needed.

- TEST URLS (mocked)
  See:
  - @pytest.mark.urls('core.urls_api')
    This tells the test to look at the 
    core.urls_api file.
==========================================
"""


#==========================================
# SET UP the TEST DATABASE
#==========================================
# Set up the test database for this session of tests
@pytest.fixture(scope='session')
def django_db_setup():
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': '127.0.0.1',
        'NAME': 'ivault2_unit_test',
    }

#==========================================
# CREATE ASSET
# The Asset create fprocess is complex and
# handled by the uploader module.
# See:   test_uploader_images.py
#==========================================

#==========================================
# READ SINGLE ASSET by ID
# ENDPOINT: /api/asset/?id=80450
#==========================================
# Tell pytest where to look for the url routing
# Then tell pytest to allow access to the database
@pytest.mark.urls('core.urls_api')
@pytest.mark.django_db
def test_api_asset_get_single_by_id(client):
    asset_id = 8508
    headerAuth = 'Token 8b1c628ddbcf52abfa741210bc2416b941d18033'
    resp = client.get('/api/asset/?id=80450', HTTP_AUTHORIZATION=headerAuth, HTTP_ACCEPT='application/json')
    data = json.loads(resp.content)
    #print('#===============================================')
    #print(' READ SINGLE ASSET by ID ')
    #print('#===============================================')
    #pprint(data)
    assert resp.status_code == 200
    assert  isinstance(data['success'], str)
    assert  isinstance(data['data']['id'], int)
    assert  isinstance(data['data']['fileName'], str)
    assert  isinstance(data['data']['search_string'], str)
    assert  isinstance(data['data']['options'], list)
    assert  isinstance(data['data']['timestamp'], str)

#==========================================
# READ SINGLE ASSET by FileName
# ENDPOINT: /api/asset/?id=UnitTest_upload_image.png
#==========================================
# Tell pytest where to look for the url routing
# Then tell pytest to allow access to the database
@pytest.mark.urls('core.urls_api')
@pytest.mark.django_db
def test_api_asset_get_single_by_filename(client):
    asset_filename = 'UnitTest_upload_image.png'
    headerAuth = 'Token 8b1c628ddbcf52abfa741210bc2416b941d18033'
    resp = client.get('/api/asset/?fileName='+asset_filename, HTTP_AUTHORIZATION=headerAuth, HTTP_ACCEPT='application/json')
    data = json.loads(resp.content)
    #print('#===============================================')
    #print(' READ SINGLE ASSET by FileName ')
    #print('#===============================================')
    #pprint(data)

    assert resp.status_code == 200
    assert  isinstance(data['success'], str)
    assert  isinstance(data['data']['id'], int)
    assert  isinstance(data['data']['fileName'], str)
    assert  isinstance(data['data']['search_string'], str)
    assert  isinstance(data['data']['options'], list)
    assert  isinstance(data['data']['timestamp'], str)

#==========================================
# READ MULTIPLE ASSETS by Comma Sep'd IDs
# ENDPOINT: /api/asset/?ids=8508,8450,8448
#==========================================
# Tell pytest where to look for the url routing
# Then tell pytest to allow access to the database
@pytest.mark.urls('core.urls_api')
@pytest.mark.django_db
def test_api_asset_get_multi_by_ids(client):
    asset_ids = '8508,8450,8448'
    headerAuth = 'Token 8b1c628ddbcf52abfa741210bc2416b941d18033'
    resp = client.get('/api/asset/?ids='+asset_ids, HTTP_AUTHORIZATION=headerAuth, HTTP_ACCEPT='application/json')
    data = json.loads(resp.content)
    assert resp.status_code == 200
    assert  isinstance(data['success'], str)
    assert  isinstance(data['data'], list)
    assert  isinstance(data['count'], int)
    assert  isinstance(data['ids'], list)
    assert  isinstance(data['assetFileNames'], list)
    assert  isinstance(data['data'][0], dict)
    assert  isinstance(data['data'][0]['id'], int)
    assert  isinstance(data['data'][0]['fileName'], str)
    assert  isinstance(data['data'][0]['options'], list)

#===============================================
# READ MULTIPLE ASSETS by Comma Sep'd FileNames
# ENDPOINT: /api/asset/?ids=<filename>,<filename>,<filename>
#===============================================
# Tell pytest where to look for the url routing
# Then tell pytest to allow access to the database
@pytest.mark.urls('core.urls_api')
@pytest.mark.django_db
def test_api_asset_get_multi_by_ids(client):
    asset_filenames = 'UnitTest_upload_image.png,11_PAL_TMF_BSI_72M.jpg,174P20_R1_300s.jpg'
    headerAuth = 'Token 8b1c628ddbcf52abfa741210bc2416b941d18033'
    resp = client.get('/api/asset/?fileNames='+asset_filenames, HTTP_AUTHORIZATION=headerAuth, HTTP_ACCEPT='application/json')
    data = json.loads(resp.content)
    #print('#===============================================')
    #print(' READ MULTIPLE ASSETS by Comma Sepd FileNames ')
    #print('#===============================================')
    #pprint(data)
    assert resp.status_code == 200
    assert  isinstance(data['success'], str)
    assert  isinstance(data['data'], list)
    assert  isinstance(data['count'], int)
    assert  isinstance(data['ids'], list)
    assert  isinstance(data['assetFileNames'], list)
    assert  isinstance(data['data'][0], dict)
    assert  isinstance(data['data'][0]['id'], int)
    assert  isinstance(data['data'][0]['fileName'], str)
    assert  isinstance(data['data'][0]['options'], list)





