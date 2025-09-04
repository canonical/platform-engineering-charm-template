# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

#########################
#                       #
#   Required settings   #
#                       #
#########################

import json
import os

# see https://github.com/netbox-community/netbox/issues/15427
if 'DJANGO_AWS_ENDPOINT_URL' in os.environ:
    os.environ['AWS_ENDPOINT_URL'] = os.environ['DJANGO_AWS_ENDPOINT_URL']

# This is a list of valid fully-qualified domain names (FQDNs) for the NetBox server. NetBox will not permit write
# access to the server via any other hostnames. The first FQDN in the list will be treated as the preferred name.
#
ALLOWED_HOSTS = json.loads(os.environ.get("DJANGO_ALLOWED_HOSTS", "[]"))

# PostgreSQL database configuration. See the Django documentation for a complete list of available parameters:
#   https://docs.djangoproject.com/en/stable/ref/settings/#databases

DATABASE = {
    'ENGINE': 'django.db.backends.postgresql',  # Database engine
    "NAME": os.environ.get("POSTGRESQL_DB_NAME"),
    "USER": os.environ.get("POSTGRESQL_DB_USERNAME"),
    "PASSWORD": os.environ.get("POSTGRESQL_DB_PASSWORD"),
    "HOST": os.environ.get("POSTGRESQL_DB_HOSTNAME"),
    "PORT": int(os.environ.get("POSTGRESQL_DB_PORT", "5432")),
    'CONN_MAX_AGE': 300,      # Max database connection age
}

# Redis database settings. Redis is used for caching and for queuing background tasks such as webhook events. A separate
# configuration exists for each. Full connection details are required in both sections, and it is strongly recommended
# to use two separate database IDs.

REDIS = {
    'tasks': {
        'HOST': os.environ.get("REDIS_DB_HOSTNAME"),
        'PORT': os.environ.get("REDIS_DB_PORT", "6379"),
        # Comment out `HOST` and `PORT` lines and uncomment the following if using Redis Sentinel
        # 'SENTINELS': [('mysentinel.redis.example.com', 6379)],
        # 'SENTINEL_SERVICE': 'netbox',
        'USERNAME': os.environ.get("REDIS_DB_USERNAME", ""),
        'PASSWORD': os.environ.get("REDIS_DB_PASSWORD", ""),
        'DATABASE': 0,
        'SSL': False,
        # Set this to True to skip TLS certificate verification
        # This can expose the connection to attacks, be careful
        # 'INSECURE_SKIP_TLS_VERIFY': False,
        # Set a path to a certificate authority, typically used with a self signed certificate.
        # 'CA_CERT_PATH': '/etc/ssl/certs/ca.crt',
    },
    'caching': {
        'HOST': os.environ.get("REDIS_DB_HOSTNAME"),
        'PORT': os.environ.get("REDIS_DB_PORT", "6379"),
        # Comment out `HOST` and `PORT` lines and uncomment the following if using Redis Sentinel
        # 'SENTINELS': [('mysentinel.redis.example.com', 6379)],
        # 'SENTINEL_SERVICE': 'netbox',
        'USERNAME': os.environ.get("REDIS_DB_USERNAME", ""),
        'PASSWORD': os.environ.get("REDIS_DB_PASSWORD", ""),
        'DATABASE': 1,
        'SSL': False,
        # Set this to True to skip TLS certificate verification
        # This can expose the connection to attacks, be careful
        # 'INSECURE_SKIP_TLS_VERIFY': False,
        # Set a path to a certificate authority, typically used with a self signed certificate.
        # 'CA_CERT_PATH': '/etc/ssl/certs/ca.crt',
    }
}

# This key is used for secure generation of random numbers and strings. It must never be exposed outside of this file.
# For optimal security, SECRET_KEY should be at least 50 characters in length and contain a mix of letters, numbers, and
# symbols. NetBox will not run without this defined. For more information, see
# https://docs.djangoproject.com/en/stable/ref/settings/#std:setting-SECRET_KEY

# It is less than 50 characters in the 12 factor. Double the size.
# FIXME This is becausse currently the 12 factor in sending a small secret_key. Pending to fix.
SECRET_KEY = os.environ['DJANGO_SECRET_KEY'] * 2


#########################
#                       #
#   Optional settings   #
#                       #
#########################

# Specify one or more name and email address tuples representing NetBox administrators. These people will be notified of
# application errors (assuming correct email settings are provided).
ADMINS = [
    # ('John Doe', 'jdoe@example.com'),
]

# Permit the retrieval of API tokens after their creation.
ALLOW_TOKEN_RETRIEVAL = False

# Enable any desired validators for local account passwords below. For a list of included validators, please see the
# Django documentation at https://docs.djangoproject.com/en/stable/topics/auth/passwords/#password-validation.
AUTH_PASSWORD_VALIDATORS = [
    # {
    #     'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    #     'OPTIONS': {
    #         'min_length': 10,
    #     }
    # },
]

# Base URL path if accessing NetBox within a directory. For example, if installed at https://example.com/netbox/, set:
# BASE_PATH = 'netbox/'
BASE_PATH = os.environ.get("DJANGO_BASE_PATH", "")

# API Cross-Origin Resource Sharing (CORS) settings. If CORS_ORIGIN_ALLOW_ALL is set to True, all origins will be
# allowed. Otherwise, define a list of allowed origins using either CORS_ORIGIN_WHITELIST or
# CORS_ORIGIN_REGEX_WHITELIST. For more information, see https://github.com/ottoyiu/django-cors-headers
CORS_ORIGIN_ALLOW_ALL = False
CORS_ORIGIN_WHITELIST = [
    # 'https://hostname.example.com',
]
CORS_ORIGIN_REGEX_WHITELIST = [
    # r'^(https?://)?(\w+\.)?example\.com$',
]

# The name to use for the CSRF token cookie.
CSRF_COOKIE_NAME = 'csrftoken'

# Set to True to enable server debugging. WARNING: Debugging introduces a substantial performance penalty and may reveal
# sensitive information about your installation. Only enable debugging while performing testing. Never enable debugging
# on a production system.
DEBUG = os.environ.get("DJANGO_DEBUG", "false") == "true"

# Set the default preferred language/locale
DEFAULT_LANGUAGE = 'en-us'

# Email settings
EMAIL = {
    'SERVER': 'localhost',
    'PORT': 25,
    'USERNAME': '',
    'PASSWORD': '',
    'USE_SSL': False,
    'USE_TLS': False,
    'TIMEOUT': 10,  # seconds
    'FROM_EMAIL': '',
}

# Localization
ENABLE_LOCALIZATION = False

# Exempt certain models from the enforcement of view permissions. Models listed here will be viewable by all users and
# by anonymous users. List models in the form `<app>.<model>`. Add '*' to this list to exempt all models.
EXEMPT_VIEW_PERMISSIONS = [
    # 'dcim.site',
    # 'dcim.region',
    # 'ipam.prefix',
]

# HTTP proxies NetBox should use when sending outbound HTTP requests (e.g. for webhooks).
# HTTP_PROXIES = {
#     'http': 'http://10.10.1.10:3128',
#     'https': 'http://10.10.1.10:1080',
# }

# IP addresses recognized as internal to the system. The debugging toolbar will be available only to clients accessing
# NetBox from an internal IP.
INTERNAL_IPS = ('127.0.0.1', '::1')

# Enable custom logging. Please see the Django documentation for detailed guidance on configuring custom logs:
#   https://docs.djangoproject.com/en/stable/topics/logging/
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'normal': {
            'format': '%(asctime)s %(name)s %(levelname)s: %(message)s'
        },
    },
    'handlers': {
        "console": {
            "class": "logging.StreamHandler",
            'level': 'DEBUG',
            'formatter': 'normal',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'netbox': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}

# Automatically reset the lifetime of a valid session upon each authenticated request. Enables users to remain
# authenticated to NetBox indefinitely.
LOGIN_PERSISTENCE = False

# Setting this to True will permit only authenticated users to access any part of NetBox. By default, anonymous users
# are permitted to access most data in NetBox but not make any changes.
LOGIN_REQUIRED = False

# The length of time (in seconds) for which a user will remain logged into the web UI before being prompted to
# re-authenticate. (Default: 1209600 [14 days])
LOGIN_TIMEOUT = None

# The view name or URL to which users are redirected after logging out.
LOGOUT_REDIRECT_URL = 'home'

# The file path where uploaded media such as image attachments are stored. A trailing slash is not needed. Note that
# the default value of this setting is derived from the installed location.
# MEDIA_ROOT = '/opt/netbox/netbox/media'

# Expose Prometheus monitoring metrics at the HTTP endpoint '/metrics'
METRICS_ENABLED = False

# Enable installed plugins. Add the name of each plugin to the list.
PLUGINS = []

# Plugins configuration settings. These settings are used by various plugins that the user may have installed.
# Each key in the dictionary is the name of an installed plugin and its value is a dictionary of settings.
# PLUGINS_CONFIG = {
#     'my_plugin': {
#         'foo': 'bar',
#         'buzz': 'bazz'
#     }
# }

# This repository is used to check whether there is a new release of NetBox available. Set to None to disable the
# version check or use the URL below to check for release in the official NetBox repository.
RELEASE_CHECK_URL = None
# RELEASE_CHECK_URL = 'https://api.github.com/repos/netbox-community/netbox/releases'

# The file path where custom reports will be stored. A trailing slash is not needed. Note that the default value of
# this setting is derived from the installed location.
# REPORTS_ROOT = '/opt/netbox/netbox/reports'

# Maximum execution time for background tasks, in seconds.
RQ_DEFAULT_TIMEOUT = 300

# The file path where custom scripts will be stored. A trailing slash is not needed. Note that the default value of
# this setting is derived from the installed location.
# SCRIPTS_ROOT = '/opt/netbox/netbox/scripts'

# The name to use for the session cookie.
SESSION_COOKIE_NAME = 'sessionid'

# By default, NetBox will store session data in the database. Alternatively, a file path can be specified here to use
# local file storage instead. (This can be useful for enabling authentication on a standby instance with read-only
# database access.) Note that the user as which NetBox runs must have read and write permissions to this path.
SESSION_FILE_PATH = None

# Time zone (default: UTC)
TIME_ZONE = 'UTC'

# Date/time formatting. See the following link for supported formats:
# https://docs.djangoproject.com/en/stable/ref/templates/builtins/#date
DATE_FORMAT = 'N j, Y'
SHORT_DATE_FORMAT = 'Y-m-d'
TIME_FORMAT = 'g:i a'
SHORT_TIME_FORMAT = 'H:i:s'
DATETIME_FORMAT = 'N j, Y g:i a'
SHORT_DATETIME_FORMAT = 'Y-m-d H:i'

# Remote authentication support
REMOTE_AUTH_ENABLED = False
if "SAML_ENTITY_ID" in os.environ:
    REMOTE_AUTH_ENABLED = True
    REMOTE_AUTH_BACKEND = 'social_core.backends.saml.SAMLAuth'

    SOCIAL_AUTH_SAML_SP_ENTITY_ID = os.environ.get("DJANGO_SAML_SP_ENTITY_ID")
    SOCIAL_AUTH_SAML_ENABLED_IDPS = {
        "saml": {
            "entity_id": os.environ.get("SAML_ENTITY_ID"),
            "url": os.environ.get("SAML_SINGLE_SIGN_ON_REDIRECT_URL"),
            "x509cert": os.environ.get("SAML_SIGNING_CERTIFICATE"),
            "attr_user_permanent_id": os.environ.get("DJANGO_SAML_USERNAME"),
            "attr_username": os.environ.get("DJANGO_SAML_USERNAME"),
        }
    }
    if os.environ.get("DJANGO_SAML_EMAIL"):
        SOCIAL_AUTH_SAML_ENABLED_IDPS["saml"]["attr_email"] = os.environ["DJANGO_SAML_EMAIL"]

    # The next variables are mandatory. They are set to an arbitrary value so SAML does not fail.
    SOCIAL_AUTH_SAML_ORG_INFO = {
        "en-US": {
            "name": "example",
            "displayname": "Example Inc.",
            "url": "http://netbox.example.com"
        }
    }
    SOCIAL_AUTH_SAML_TECHNICAL_CONTACT = {
        "givenName": "Tech Gal",
        "emailAddress": "technical@example.com"
    }
    SOCIAL_AUTH_SAML_SUPPORT_CONTACT = {
        "givenName": "Support Guy",
        "emailAddress": "support@example.com"
    }

    # SAML SP certificates (AuthnRequestsSigned) not implemented for the charm.
    # It is necessary to have SOCIAL_AUTH_SAML_SP_PUBLIC_CERT and_AUTH_SAML_SP_PRIVATE_KEY
    # defined as strings, otherwise the saml library will fail.
    SOCIAL_AUTH_SAML_SP_PUBLIC_CERT = ""
    SOCIAL_AUTH_SAML_SP_PRIVATE_KEY = ""

REMOTE_AUTH_AUTO_CREATE_USER = True
REMOTE_AUTH_DEFAULT_GROUPS = []
REMOTE_AUTH_DEFAULT_PERMISSIONS = {}

# By default, uploaded media is stored on the local filesystem. Using Django-storages is also supported. Provide the
# class path of the storage driver in STORAGE_BACKEND and any configuration options in STORAGE_CONFIG.
# For the NetBox charm, the only supported option is S3 storage.
if 'S3_ACCESS_KEY' in os.environ:
    STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
        'access_key': os.environ.get('S3_ACCESS_KEY'),
        'secret_key': os.environ.get('S3_SECRET_KEY'),
        'bucket_name': os.environ.get('S3_BUCKET'),
        'region_name': os.environ.get('S3_REGION'),
        'endpoint_url': os.environ.get('S3_ENDPOINT'),
        'addressing_style': os.environ.get('S3_ADDRESSING_STYLE'),
        },
    },
}
