from django.http import HttpRequest, HttpResponse, JsonResponse
from django.db import models
from core import settings
from tagBot import functions as tagbotFunc
from core.serializers import AssetSerializer
from iv_logger.models import IvaultLog 
from pprint import pprint
import json
import pytest
import datetime
import inspect

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


@pytest.mark.django_db
def test_tagbot_AME_72M_option_objs_loaded():
    # Mock the request object
    mode='ALL'
    filename = 'AME_72M.jpg'
    resp = tagbotFunc.process_filename_codes(filename, mode)
    #print('==== TAGBOT TEST DATA ====')
    #pprint(resp)
    assert resp['optionsData'][0]['groupName'] == 'Photo Dimension'
    assert resp['optionsData'][1]['groupName'] == 'Photo Resolution (DPI)'
    assert resp['optionsData'][2]['groupName'] == 'Drawer Front'
    assert resp['optionsData'][3]['groupName'] == 'Door Style Name'

#testSet = ['3184', '3089', '3166']

@pytest.mark.django_db
def test_tagbot_pkl_logic_variations():
    # Mock the request object
    mode='SFK'
    filename = '72M_TTT_BYY.jpg'
    resp = tagbotFunc.process_filename_codes(filename, mode)
    #data = json.loads(resp)
    #print('==== TAGBOT TEST DATA ====')
    #pprint(resp)
    latest_id = IvaultLog.objects.latest('id').id
    log = IvaultLog.objects.get(id=int(latest_id) )
    print('==== FETCHED TEST LOG DATA=====')
    pprint(log.data)
    # For 72M  (mode: - any-)
    testSet = ['233', '240'] 
    assert set(testSet).issubset(resp['ids']) == True
    # For TTT_BYY (mode:SFK)
    testSet = ['99990102']
    assert set(testSet).issubset(resp['ids']) == True
    # For mode:SFK with no W
    testSet = ['1270']
    assert set(testSet).issubset(resp['ids']) == True
    # Confirm Logger is logging this action
    assert log.data == 'TAGBOT file:72M_TTT_BYY |   Logic:IF W THEN 1273 ELSE 1270  Logic:IF TTT,-BYY THEN 99990100 ELSE 99990102 IDs:233,240,1270,99990102,'

@pytest.mark.django_db
def test_tagbot_alpha_code_combo_for_1_id():
    # Mock the request object
    mode = "ALL"
    filename = "ASR_AME_SDF.jpg"
    resp = tagbotFunc.process_filename_codes(filename, mode)
    # For ASR_AME_SDF  combo
    testSet = ['1267']
    assert set(testSet).issubset(resp['ids'])
    # For ASR_AME_SDF, the non combo part
    # Duplictes removed (1267 would have been twice)
    testSet = ['999', '2496', '1267', '3044']
    assert testSet == resp['ids']

@pytest.mark.django_db
def test_tagbot_multiple_ids_combined_with_logic_forTrue():
    # Mock the request object
    mode='SFK'
    filename = 'AME_72M_PRA_BYY_TEST_W_CCH_TTT_PDQ.jpg'
    get_request = rf.get('/tagbot/test/?filename=AME_72M_PRA_BYY_TEST_W_CCH_TTT_PDQ.jpg&mode=SFK')
    resp = tagbotFunc.process_filename_codes(filename, mode)
    """
    Based on ~Logic from tagbotmappingtable
    CONDISTIONS:
        Mode ID: 2 (SFK)
        LOGIC: _IF: TTT,-BYY _THEN: 99990100 _ELSE: 99990102
        BYY IS in filename so expecting inclusion of ID: 99990102
    """
    testSet = ['99990100']
    assert set(testSet).issubset(resp['ids']) == False
    testSet = ['99990102']
    assert set(testSet).issubset(resp['ids']) == True

@pytest.mark.django_db
def test_tagbot_multiple_ids_combined_with_logic_forTrue():
    # Mock the request object
    mode='SFK'
    filename = 'AME_72M_PRA_TEST_W_CCH_TTT_PDQ.jpg'
    get_request = rf.get('/tagbot/test/?filename=AME_72M_PRA_BYY_TEST_W_CCH_TTT_PDQ.jpg&mode=SFK')
    resp = tagbotFunc.process_filename_codes(filename, mode)
    """
    Based on ~Logic from tagbotmappingtable
    CONDISTIONS:
        Mode ID: 2 (SFK)
        LOGIC: _IF: TTT,-BYY _THEN: 99990100 _ELSE: 99990102
        BYY IS NOT in filename so expecting inclusion of ID: 99990100
    """
    testSet = ['99990100']
    assert set(testSet).issubset(resp['ids']) == True
    testSet = ['99990102']
    assert set(testSet).issubset(resp['ids']) == False
























