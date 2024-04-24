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


"""
TEST API ENDPOINT: GET /api/asset/option?id=80450
"""
# Tell pytest where to look for the url routing
@pytest.mark.urls('core.urls_api')
# Then tell pytest to allow access to the database
@pytest.mark.django_db
# Create the test function with the `client` dependancy injection
def test_asset_option(client):
    # Config the vars
    asset_id = 8508
    headerAuth = 'Token 8b1c628ddbcf52abfa741210bc2416b941d18033'
    # use the client (get, put, post delete)
    resp = client.get('/api/asset/option/filtered/any', HTTP_AUTHORIZATION=headerAuth, HTTP_ACCEPT='application/json')
    # COnvert resp to json data
    data = json.loads(resp.content)
    #print('================================')
    #pprint(data)
    #pprint(resp.status_code)
    #print('================================')
    assert resp.status_code == 200
    #assert data['success'] == True
    #assert  isinstance(data['success'], bool)
    #assert  isinstance(data['data']['id'], int)
    #assert  isinstance(data['data']['groupName'], str)
    #assert  isinstance(data['data']['definition'], str)
# ---------------------------------------------





"""
TEST API ENDPOINT: /api/asset/option/group/
"""
@pytest.mark.urls('core.urls_api')
@pytest.mark.django_db
def test_asset_option_group(client):
    headerAuth = 'Token 8b1c628ddbcf52abfa741210bc2416b941d18033'
    resp = client.get('/api/asset/option/group/', HTTP_AUTHORIZATION=headerAuth, HTTP_ACCEPT='application/json')
    data = json.loads(resp.content)
    #print('================================')
    #pprint(data)
    #pprint(resp.status_code)
    #print('================================')
    assert resp.status_code == 200
    assert data['success'] == True
    assert  isinstance(data['success'], bool)
    assert  isinstance(data['optionGroups'], list)
    option_groups_list = data['optionGroups']
    first_group_in_list = option_groups_list[0]
    assert  isinstance(first_group_in_list, dict)
    assert  isinstance(first_group_in_list['id'], int)
    assert  isinstance(first_group_in_list['groupName'], str)
    assert  isinstance(first_group_in_list['name'], str)
    assert  isinstance(first_group_in_list['code'], int)
# ---------------------------------------------

"""
TEST API ENDPOINT: /api/asset/option/group/filtered?filteringString='+filtering_str
"""
@pytest.mark.urls('core.urls_api')
@pytest.mark.django_db
def test_asset_option_group_filtered(client):
    filtering_str = 'drawer'
    headerAuth = 'Token 8b1c628ddbcf52abfa741210bc2416b941d18033'
    resp = client.get('/api/asset/option/group/filtered?filteringString='+filtering_str,
                       HTTP_AUTHORIZATION=headerAuth, HTTP_ACCEPT='application/json')
    data = json.loads(resp.content)
    # print('================================')
    # pprint(data)
    # pprint(resp.status_code)
    # print('================================')
    assert resp.status_code == 200
    assert data['success'] == True
    assert  isinstance(data['success'], bool)
    assert  isinstance(data['optionGroups'], list)
    option_groups_list = data['optionGroups']
    first_group_in_list = option_groups_list[0]
    assert  isinstance(first_group_in_list['groupName'], str)
    assert filtering_str.lower() in first_group_in_list['groupName'].lower()

# ---------------------------------------------

"""
TEST API ENDPOINT: /api/asset/option/filtered/any?filteringString=+filtering_str
"""
@pytest.mark.urls('core.urls_api')
@pytest.mark.django_db
def test_asset_option_filtered_any(client):
    filtering_str = 'tall'
    headerAuth = 'Token 8b1c628ddbcf52abfa741210bc2416b941d18033'
    resp = client.get('/api/asset/option/filtered/any?filteringString='+filtering_str,
                       HTTP_AUTHORIZATION=headerAuth, HTTP_ACCEPT='application/json')
    data = json.loads(resp.content)
    # print('================================')
    # print(' test_asset_option_filtered_any')
    # print('================================')
    # pprint(data)
    # pprint(resp.status_code)
    # print('================================')
    assert resp.status_code == 200
    assert data['success'] == True
    assert  isinstance(data['success'], bool)
    assert  isinstance(data['optionGroups'], list)
    option_groups_list = data['optionGroups']
    first_group_in_list = option_groups_list[0]
    assert  isinstance(first_group_in_list['groupName'], str)
    assert  isinstance(first_group_in_list['definition'], str)
    filtering_term_found = False
    if first_group_in_list['groupName'].lower() or first_group_in_list['definition'].lower():
      filtering_term_found = True
    assert filtering_term_found == True 

# ---------------------------------------------


"""
TEST API ENDPOINT: /api/asset/option/group/values/?groupName=General
"""
@pytest.mark.urls('core.urls_api')
@pytest.mark.django_db
def test_asset_option_group_values(client):
    optionGroupName = 'General'
    headerAuth = 'Token 8b1c628ddbcf52abfa741210bc2416b941d18033'
    resp = client.get('/api/asset/option/group/values/?optionGroupName='+optionGroupName, 
                       HTTP_AUTHORIZATION=headerAuth, HTTP_ACCEPT='application/json')
    data = json.loads(resp.content)
    #print('================================')
    #print(' test_asset_option_group_values')
    #print('================================')
    #pprint(data)
    #pprint(resp.status_code)
    #print('================================')
    assert resp.status_code == 200
    assert data['success'] == True
    assert  isinstance(data['success'], bool)
    assert  isinstance(data['data'], list)
    option_definition_list = data['data']
    assert  isinstance(option_definition_list[0]['id'], int)
    assert  isinstance(option_definition_list[0]['groupName'], str)
    assert  isinstance(option_definition_list[0]['definition'], str)
    assert  option_definition_list[0]['groupName'].lower() == optionGroupName.lower()

# ---------------------------------------------





