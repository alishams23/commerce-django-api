import os
from dotenv import load_dotenv
from datetime import timedelta
from config.settings import base

dotenv_path = os.path.join(base.BASE_DIR,".env.development")
load_dotenv(dotenv_path)

from .base import *

DEBUG = os.environ.get("DEBUG")

# allowed_hosts = ""
ALLOWED_HOSTS = ['*']

# csrf_trusted_origins = os.environ.get("DJANGO_CSRF_TRUSTED_ORIGINS", "")
# CORS_ALLOWED_ORIGINS = tuple(url.strip() for url in csrf_trusted_origins.split(","))
# CSRF_TRUSTED_ORIGINS = ["*"]


SECRET_KEY = os.environ.get("SECRET_KEY")


STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(base.BASE_DIR, 'static/')

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(base.BASE_DIR, 'media/') 



SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=7),   
    "REFRESH_TOKEN_LIFETIME": timedelta(days=14),     
    "ROTATE_REFRESH_TOKENS": True,                   
    "BLACKLIST_AFTER_ROTATION": True,                
    "AUTH_HEADER_TYPES": ("Token",),                
}

#region log config
# LOGGING = {
#     "version": 1,
#     "disable_existing_loggers": False,
#     'formatters': {
#         'simple': {
#             'format': '[%(asctime)s] %(levelname)s|%(name)s|%(message)s',
#             'datefmt': '%Y-%m-%d %H:%M:%S',
#         },
#     },
#     "handlers": {
#         'console': {
#             'level': 'DEBUG',
#             'class': 'logging.StreamHandler',
#             'formatter': 'simple'
#     },
#     "loggers": {
#         "root": {
#             "handlers": ["console"],
#             "level": "DEBUG",
#         },
#         "django": {
#             "handlers": ["console"],
#             "level": "DEBUG",
#             "propagate": False,
#         },
#         'django.request': {
#             'handlers': ['console'],
#             'level': 'DEBUG',
#             'propagate': True,
#         },
#     },
#     }
# }
#
#endregion

CORS_ALLOW_ALL_ORIGINS = True
