from django.http import HttpRequest, HttpResponse, JsonResponse
from core import settings
from iv_logger.models import IvaultLog 
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
"""
[99,108,118,171,226,231,232,237,240,454,838,1021,1041,1085,1124,1127,1129,1130,1132,1140,1145,1267,1270,1274,1275,3056]
"""


#==========================================
# CREATE ASSET
# The Asset create fprocess is complex and
# handled by the uploader module.
# See:   test_uploader_images.py
#==========================================

#==========================================
# UPDATE (PUT) SINGLE ASSET by ID
# ENDPOINT: /api/asset/?id=80450  'fileName': 'UnitTest_upload_image.png',
#==========================================
# Tell pytest where to look for the url routing
# Then tell pytest to allow access to the database
@pytest.mark.urls('core.urls_api')
@pytest.mark.django_db
def test_api_asset_get_single_by_id(client):
    asset_id = 8508
    payload_dict = {
        'id': asset_id,
        'fileName': 'UnitTest_upload_image.png',
        'options': [1021,3057,1275,1274,1275,3056]
    }
    headerAuth = 'Token 8b1c628ddbcf52abfa741210bc2416b941d18033'
    preUpdateResp = client.put('/api/asset/', data=payload_dict, content_type='application/json', HTTP_AUTHORIZATION=headerAuth,)
    preUpdateData = json.loads(preUpdateResp.content)
    #print('#===============================================')
    #print(' UPDATE (PUT) SINGLE ASSET by ID '+str(asset_id))
    #print('#===============================================')
    #pprint(preUpdateData)
    #print('#===============================================')
    #print(' RELOAD THE UPDATED ASSET  '+str(asset_id) )
    #print('#===============================================')    

    postUpdateResp = client.get('/api/asset/?id='+str(asset_id), HTTP_AUTHORIZATION=headerAuth, HTTP_ACCEPT='application/json')
    postUpdateData = json.loads(postUpdateResp.content)

    latest_id = IvaultLog.objects.latest('id').id
    log = IvaultLog.objects.get(id=int(latest_id) )
    print('==== FETCHED TEST LOG DATA=====')
    pprint(log.data)
    
    assert preUpdateResp.status_code == 200
    assert postUpdateResp.status_code == 200
    assert preUpdateData['data']['fileName'] ==  postUpdateData['data']['fileName']
    assert preUpdateData['data']['id'] ==  postUpdateData['data']['id']
    assert preUpdateData['data']['options'] ==  postUpdateData['data']['options']
    assert preUpdateData['data']['search_string'] ==  postUpdateData['data']['search_string']
    # Ensure logging is working
    assert 'UPDATE Asset' in log.data
    assert 'FILENAME:UnitTest_upload_image.png' in log.data
    assert 'SEARCH_STRING:--1021--3057--1275--1274--1275--3056--' in log.data


    




















