# Django settings for pimp project.
import os
import djcelery
import distutils.util as du
import uuid

djcelery.setup_loader()

CELERYD_LOG_COLOR = False

DEBUG = True
TEMPLATE_DEBUG = DEBUG

r_path = '/usr/local/bin'
os.environ['PATH'] += os.pathsep + r_path
print os.environ['PATH']

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ['PIMP_BASE_DIR'] = BASE_DIR

# Set to True to enable registration
REGISTRATION_OPEN = False

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

EMAIL_HOST = 'mail-relay.gla.ac.uk'
# EMAIL_USE_TLS = True
# EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

DEFAULT_FROM_EMAIL = 'wwcrc-gp-noreply@glasgow.ac.uk'

# EMAIL_FILE_PATH = '/opt/django/projects/django_projects/tmp/app-messages'

MANAGERS = ADMINS

DATABASE_NAME = '/Users/Karen/pimp/django_projects/pimp/sqlite3_frank.db'
# DATABASE_NAME = 'frank_dev'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        #'ENGINE': 'django.db.backends.mysql',
        'NAME': DATABASE_NAME,
        #'NAME': '/Users/Karen/pimp/django_projects/pimp/sqlite3.db',                      # Or path to database file if using sqlite3.
        #'USER': 'root',                      # Not used with sqlite3.
        #'PASSWORD': 'p01y0m1c5',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

os.environ['PIMP_DATABASE_NAME'] = DATABASE_NAME
os.environ['PIMP_DATABASE_ENGINE'] = 'django.db.backends.sqlite3'
os.environ['R_LIBS_USER'] = '/Users/Karen/pimp/packrat/lib/x86_64-apple-darwin15.5.0/3.3.1'

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
TESTING = False
randomUUID = str(uuid.uuid4())
TEST_MEDIA_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'TESTDATA_' + randomUUID)
NORMAL_MEDIA_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'pimp_data')
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
SECRET_KEY = 'a5s!nh^1=tq3a4)jbe07*$nv6npve6d%a7nn6(8g#la)lp6oh('

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
    'django_spaghetti',
)

SPAGHETTI_SAUCE = {
  'apps':['auth','polls','frank','data','fileupload','projects','experiments','groups','compound'],
  'show_fields':False,
  'exclude':{'auth':['user']}
}


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
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            # logging handler that outputs log messages to terminal
            'class': 'logging.StreamHandler',
        #    'level': 'DEBUG', # message level to be written to console
            'level': 'ERROR', # message level to be written to console
        
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        '': {
            # this sets root level logger to log debug and higher level
            # logs to console. All other loggers inherit settings from
            # root level logger.
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False, # this tells logger to send logging message
                                # to its parent (will send if set to True)
        },
        'django.db': {
            # django also has database level logging
        },
    }
}

RSCRIPT_PATH = '/usr/local/bin/Rscript'

PROFILE_LOG_BASE = os.path.dirname(BASE_DIR)
