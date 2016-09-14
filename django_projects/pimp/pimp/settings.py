# Django settings for pimp project.
import os
import sys
import uuid

import djcelery
import distutils.util as du

def getNeededString(name):
    if not os.environ.has_key(name):
        raise Exception('Environment variable ' + name + ' is needed but is not defined')
    return os.environ[name]

def getString(name, default):
    if not os.environ.has_key(name):
        return default
    return os.environ[name]

def getBool(name, default):
    if not os.environ.has_key(name):
        return default
    return bool(du.strtobool(os.environ[name]))

def getList(name, default):
    if not os.environ.has_key(name):
        return default
    return os.environ[name].split(',')

djcelery.setup_loader()

CELERYD_LOG_COLOR = False

DEBUG = getBool('PIMP_DEBUG', False)
TEMPLATE_DEBUG = DEBUG

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ['PIMP_BASE_DIR'] = BASE_DIR

DJANGO_LOG_LEVEL = getString('PIMP_LOG_LEVEL', 'WARNING')
os.environ['DJANGO_LOG_LEVEL'] = DJANGO_LOG_LEVEL

# Set to True to enable registration
REGISTRATION_OPEN = False

ALLOWED_HOSTS = getList('PIMP_ALLOWED_HOSTS', ['127.0.0.1', 'localhost'])

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

EMAIL_HOST = getString('PIMP_EMAIL_HOST', None)
# EMAIL_USE_TLS = True
# EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

DEFAULT_FROM_EMAIL = getString('PIMP_DEFAULT_FROM_EMAIL', None)

# EMAIL_FILE_PATH = '/opt/django/projects/django_projects/tmp/app-messages'

MANAGERS = ADMINS

TESTING = 'test' in sys.argv
randomUUID = str(uuid.uuid4())

PIMP_DATABASE_ENGINE = getNeededString('PIMP_DATABASE_ENGINE')

if PIMP_DATABASE_ENGINE == 'django.db.backends.mysql':
    PIMP_DATABASE_NAME = getNeededString('MYSQL_DATABASE')
    PIMP_DATABASE_USER = getNeededString('MYSQL_USER')
    PIMP_DATABASE_PASSWORD = getNeededString('MYSQL_PASSWORD')
    TEST_DATABASE_NAME = 'TESTDB_' + randomUUID
    if TESTING:
        os.environ['MYSQL_DATABASE'] = TEST_DATABASE_NAME
elif PIMP_DATABASE_ENGINE == 'django.db.backends.sqlite3':
    SQLITE_DATABASE_FILENAME = getNeededString('SQLITE_DATABASE_FILENAME')
    PIMP_DATABASE_NAME = os.path.join(BASE_DIR, SQLITE_DATABASE_FILENAME)
    PIMP_DATABASE_USER = ''
    PIMP_DATABASE_PASSWORD = ''
    TEST_DATABASE_NAME = os.path.join(BASE_DIR, 'TESTDB_' + randomUUID + '.db')
    if TESTING:
        os.environ['SQLITE_DATABASE_FILENAME'] = 'TESTDB_' + randomUUID + '.db'

if TESTING:
    ACTUAL_DATABASE = TEST_DATABASE_NAME
else:
    ACTUAL_DATABASE = PIMP_DATABASE_NAME

DATABASES = {
    'default': {
        # 'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'ENGINE': PIMP_DATABASE_ENGINE,
        'NAME': PIMP_DATABASE_NAME,
        # 'NAME': '/Users/yoanngloaguen/Documents/django_projects/pimp/sqlite3.db',                      # Or path to database file if using sqlite3.
        'USER': PIMP_DATABASE_USER,                      # Not used with sqlite3.
        'PASSWORD': PIMP_DATABASE_PASSWORD,                  # Not used with sqlite3.
        'HOST': getString('PIMP_DATABASE_HOST', ''),                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': getString('PIMP_DATABASE_PORT', ''),                      # Set to empty string for default. Not used with sqlite3.
        'TEST' : {
            'NAME' : TEST_DATABASE_NAME
        },
    }
}

AUTHENTICATION_BACKENDS = ('backends.EmailOrUsernameModelBackend','django.contrib.auth.backends.ModelBackend')
# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/London'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
# TODO: Changed by Yoann to false for debug, doesn't work with timezone-aware datetimes, need to be corrected!
USE_TZ = False

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
# MEDIA_ROOT = os.path.abspath(os.path.dirname(__file__)) + '/media/'
TEST_MEDIA_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'TESTDATA_' + randomUUID)
NORMAL_MEDIA_ROOT = getString('PIMP_MEDIA_ROOT',os.path.join(os.path.dirname(BASE_DIR), 'pimp_data'))
if TESTING:
    MEDIA_ROOT = TEST_MEDIA_ROOT
else:
    MEDIA_ROOT = NORMAL_MEDIA_ROOT
os.environ['PIMP_MEDIA_ROOT'] = MEDIA_ROOT


#MEDIA_ROOT = '/opt/django/data/pimp_data/'
#MEDIA_ROOT = '/Users/yoanngloaguen/Documents/ideomWebSite/media/'
# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))) + '/static/'
#STATIC_ROOT = '/Users/yoanngloaguen/Documents/ideomWebSite/static/'

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    # '/Users/yoanngloaguen/Documents/django_projects/pimp/static/',
    os.path.join(os.path.dirname(__file__), 'static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = getNeededString('PIMP_SECRET_KEY')

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'pimp.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'pimp.wsgi.application'

TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(BASE_DIR), 'mytemplates'),
    os.path.join(os.path.dirname(os.path.dirname(BASE_DIR)), 'python_support'), 
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.static',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'django_extensions',
    'home',
    'registration',
    'projects',
    'fileupload',
    'groups',
    'experiments',
    'data',
    'compound',
    'djcelery',
    'gp_registration',
    'frank',
    # 'south',
    #'sorl.thumbnail',
    #'multiuploader',
)

ACCOUNT_ACTIVATION_DAYS = 7 # One-week activation window; you may, of course, use a different value.

# REGISTRATION_OPEN = False

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(filename)s:%(lineno)d | %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(filename)s:%(lineno)d | %(message)s'
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'class': 'logging.StreamHandler',
            'level': os.getenv('DJANGO_LOG_LEVEL', 'WARNING'),
            'formatter': 'verbose', 
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        '': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    }
}

RSCRIPT_PATH = getNeededString('PIMP_RSCRIPT_PATH')

PROFILE_LOG_BASE = getString('PROFILE_LOG_BASE', os.path.dirname(BASE_DIR))

FIXTURE_DIRS = (
    os.path.join(BASE_DIR, 'fixtures'),
)

TEST_RUNNER = 'django.test.runner.DiscoverRunner'
