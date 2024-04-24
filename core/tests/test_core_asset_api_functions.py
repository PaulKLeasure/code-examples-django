from django.http import HttpRequest, HttpResponse, JsonResponse
from django.db import models
from core import settings
from core import views_api_asset_crud as api
from core.serializers import AssetSerializer
from pprint import pprint
import json
import pytest
import datetime
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
DATABASE
SEE:  https://pytest-django.readthedocs.io/en/latest/database.html
"""
# Set up the existing test database for this session of tests
@pytest.fixture(scope='session')
def django_db_setup():
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': '127.0.0.1',
        'NAME': 'ivault2_unit_test',
    }

"""
==========================================
 Use DJANGO RequestFactory to 
 mock the response object
 eg.
   get_request = rf.get('/hello/')
   post_request = rf.post('/submit/', {'foo': 'bar'})
==========================================
"""
from django.test.client import RequestFactory
rf = RequestFactory()




#==========================================
# FETCH ASSET (singular) FUNCTION
#==========================================
@pytest.mark.django_db
def test_fetch_asset(requests_mock):
    
    asset_id = 8508
    headerAuth = 'Token 8b1c628ddbcf52abfa741210bc2416b941d18033'

    assObjById = api.fetch_asset(requests_mock, asset_id)
    if(assObjById ):
        serializedAsset = AssetSerializer(assObjById , many=False)
        SerialAssetData = serializedAsset.data

    # Confirm existance of expected types on the raw qry result
    assert isinstance(assObjById, object)
    assert isinstance(assObjById.id, int)
    assert isinstance(assObjById.fileName, models.fields.files.FieldFile)
    assert isinstance(assObjById.fileName.name, str)
    assert isinstance(assObjById.search_string, str)
    assert isinstance(assObjById.timestamp.date(), datetime.date)
    
    # Confirm options are being handled
    assert isinstance(SerialAssetData['options'], list)
    
    # Confirm each option gets serialized as a dict
    if(SerialAssetData['options'][0]):
        assert isinstance(SerialAssetData['options'][0], dict)
    
    # Confirm the options are processed into a "--" delimted string
    if(len(SerialAssetData['search_string']) > 4):
        # print('Splitting the search_string on -- delimeter:')
        # pprint(SerialAssetData['search_string'].split("--"))
        assert isinstance(SerialAssetData['search_string'].split("--"), list)


#==========================================
# FETCH ASSETS (plural) FUNCTION
#==========================================
@pytest.mark.django_db
def test_fetch_assets():
    
    # Mock the request object
    get_request = rf.get('/api/asset/?id=80450')
    resp = api.fetch_assets(get_request)
    data = json.loads(resp.content)

    assert resp.status_code == 200
    assert  isinstance(data['success'], str)
    assert  isinstance(data['data']['id'], int)
    assert  isinstance(data['data']['fileName'], str)
    assert  isinstance(data['data']['search_string'], str)
    assert  isinstance(data['data']['options'], list)
    assert  isinstance(data['data']['timestamp'], str)    


#==========================================
# FETCH ASSETS (plural) FUNCTION
#==========================================
@pytest.mark.django_db
def test_get_single_asset_by_param():
    
    # Mock the request object
    get_request = rf.get('/api/asset/?id=80450')
    resp = api.get_single_asset_by_param(get_request)
    data = json.loads(resp.content)
    assert resp.status_code == 200
    assert  isinstance(data['success'], str)
    assert  isinstance(data['data']['id'], int)
    assert  isinstance(data['data']['fileName'], str)
    assert  isinstance(data['data']['search_string'], str)
    assert  isinstance(data['data']['options'], list)
    assert  isinstance(data['data']['timestamp'], str)    


#==========================================
# fetch_assets_by_ids_string() FUNCTION
#==========================================
@pytest.mark.django_db
def test_fetch_assets_by_ids_string():
    
    # Mock the request object
    idsString="100,101,102"
    resp = api.fetch_assets_by_ids_string(idsString)
    data = json.loads(resp.content)
    assert resp.status_code == 200
    assert  isinstance(data['success'], str)
    assert  isinstance(data['data'], list)
    assert  isinstance(data['data'][0]['id'], int)
    assert  isinstance(data['data'][0]['fileName'], str)
    assert  isinstance(data['data'][0]['search_string'], str)
    assert  isinstance(data['data'][0]['options'], list)
    assert  isinstance(data['data'][0]['timestamp'], str)    


#==========================================
# fetch_assets_by_filenames_string() FUNCTION
#==========================================
@pytest.mark.django_db
def test_fetch_assets_by_filenames_string():
    
    # Mock the request object
    idsString="11_PRA_MPL_GLR-DOV_72M.jpg,11_PRA_MPL_GLR-DOV_72L.jpg,11_PRA_MPL_GLR-DOV_300S.jpg"
    resp = api.fetch_assets_by_filenames_string(idsString)
    data = json.loads(resp.content)
    assert resp.status_code == 200
    assert  isinstance(data['success'], str)
    assert  isinstance(data['data'], list)
    assert  isinstance(data['data'][0]['id'], int)
    assert  isinstance(data['data'][0]['fileName'], str)
    assert  isinstance(data['data'][0]['search_string'], str)
    assert  isinstance(data['data'][0]['options'], list)
    assert  isinstance(data['data'][0]['timestamp'], str)    






