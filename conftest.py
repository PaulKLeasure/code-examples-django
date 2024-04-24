from core import settings
import os
import sys
import pytest

sys.path.append(os.path.dirname(__file__))

#==========================================
# SET UP the TEST DATABASE
#==========================================
# Set up the test database for this session of tests
@pytest.fixture(scope='session')
def django_db_setup():
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': '127.0.0.1',
        'NAME': 'iv_unit_test',
        'USER': 'root',
        'PASSWORD': 'localDev',
    }