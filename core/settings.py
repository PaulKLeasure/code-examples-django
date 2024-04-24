"""
Django settings for iVault2 project.

Generated by 'django-admin startproject' using Django 3.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""
from pprint import pprint
import os

# Add .env handler
from dotenv import load_dotenv
load_dotenv()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

print('================== The Base DIR ================== ')
print(BASE_DIR)
print('================== The Base DIR ================== ')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '-3td+90^7+u3pir9itn=f%f)_7aoejd+lk%=upy%k$rb=(2p(b'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# For elb to work
ALLOWED_HOSTS = ['*']

# ALLOWED_HOSTS = [
# 'ivault.mac',
# 'dev.ivault2.com',
# 'dev.wellbornservices.com',
# 'ivault-dev.wellbornservices.com',
# 'ivault-stage.wellbornservices.com',
# 'ivault-api.wellbornservices.com',
# '*'
# ]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'debugtools',
    'rest_framework',
    'rest_framework_api_key',
    'rest_framework.authtoken',
    'core',
    'iv_user',
    'search',
    'searchTemplates',
    'uploader',
    'iv_logger',
    'pklextras',
    'tagBot',
    'batchTagger',
    'assetFilterAdmin',
    'altTextBot'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'builtins': [                                     # Add this section
                "debugtools.templatetags.debugtools_tags",   # Add this line
            ],
        },
    },
]

# This tells dJango to use the custom user model
AUTH_USER_MODEL  = 'iv_user.IvaultUser'

WSGI_APPLICATION = 'wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

if os.environ['DB_PORT'] is not None:
    dbPort = os.environ['DB_PORT']
else:
    dbPort=3306

print("os.environ:  ")
pprint(os.environ)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ['DB_NAME'],
        'USER': os.environ['DB_USER'],
        'PASSWORD': os.environ['DB_PASSWORD'],
        'HOST': os.environ['DB_HOST'],
        'PORT': dbPort
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, "static/")

STATIC_URL = '/static/'
STATICFILES_DIRS = [ 
    os.path.join(BASE_DIR, "static/admin"),
    os.path.join(BASE_DIR, "static/main"),
    os.path.join(BASE_DIR, "static/rest_framework"),
    os.path.join(BASE_DIR, "core/static"),
    os.path.join(BASE_DIR, "search/static"),
    os.path.join(BASE_DIR, "uploader/static"),
    ]
  
#For when primary key is not specified in model.
DEFAULT_AUTO_FIELD='django.db.models.AutoField'

# PKL Custom Account redirects
LOGIN_REDIRECT_URL  = 'home'
LOGOUT_REDIRECT_URL = 'home'
# So we can see emails via terminal
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
print(MEDIA_ROOT)
MEDIA_URL = '/media/'

S3_IVAULT_URI = os.environ['MEDIA_ASSET_URL']
S3_URI = os.environ['S3_URI']
S3_BUCKET = os.environ['S3_BUCKET']
S3_BUCKET_SUB_DIR = os.environ['S3_BUCKET_SUB_DIR']
S3_TRASH_URI = os.environ['S3_TRASH_URI']

FILE_UPLOAD_MAX_MEMORY_SIZE = 4000000
FILE_UPLOAD_MAX_MEMORY_SIZE = 2621440

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10
}

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOWED_ORIGINS = (
  'http://192.168.254.70:8080',
  'http://localhost:8080',
  'http://localhost:8800',
  'http://localhost:8090',
  'http://ivault.local:8090',
  'http://localhost',
  'https://localhost',
  'https://dev-ivault-admin.wellbornservices.com',
  'https://ivault-admin.wellbornservices.com'
)

from corsheaders.defaults import default_headers

#CORS_ALLOW_HEADERS = list(default_headers) + [
#    "my-custom-header",
#]


