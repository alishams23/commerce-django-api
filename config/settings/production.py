from datetime import timedelta
import os
from dotenv import load_dotenv
from config.settings import base

dotenv_path = os.path.join(base.BASE_DIR,".env")
load_dotenv(dotenv_path)

from .base import *

DEBUG = os.environ.get("DEBUG")

allowed_hosts = os.environ.get("ALLOWED_HOSTS", "")
ALLOWED_HOSTS = tuple(url.strip() for url in allowed_hosts.split(","))

csrf_trusted_origins = os.environ.get("CSRF_TRUSTED_ORIGINS", "")
CORS_ALLOWED_ORIGINS = tuple(url.strip() for url in csrf_trusted_origins.split(","))
CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS


SECRET_KEY = os.environ.get("SECRET_KEY")


STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(base.BASE_DIR, 'static/')

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(base.BASE_DIR, 'media/') 

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),   
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),     
    "ROTATE_REFRESH_TOKENS": False,                   
    "BLACKLIST_AFTER_ROTATION": False,                
    "AUTH_HEADER_TYPES": ("Bearer",),                
}