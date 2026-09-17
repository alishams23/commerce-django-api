import os
from datetime import timedelta

from .base import *

DEBUG = os.environ.get("DEBUG")

allowed_hosts = os.environ.get("DJANGO_ALLOWED_HOSTS", None)
ALLOWED_HOSTS = tuple(url.strip() for url in allowed_hosts.split(",")) if allowed_hosts else ['*']

csrf_trusted_origins = os.environ.get("DJANGO_CSRF_TRUSTED_ORIGINS", None)
if csrf_trusted_origins:
    CORS_ALLOWED_ORIGINS = tuple(url.strip() for url in csrf_trusted_origins.split(","))
    CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS



SECRET_KEY = os.environ.get("SECRET_KEY")



SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=7),   
    "REFRESH_TOKEN_LIFETIME": timedelta(days=14),     
    "ROTATE_REFRESH_TOKENS": True,                   
    "BLACKLIST_AFTER_ROTATION": True,                
    "AUTH_HEADER_TYPES": ("Token",),                
}

AZ_IRANIAN_BANK_GATEWAYS = {
    "GATEWAYS": {
        "ZARINPAL": {
            "MERCHANT_CODE": os.environ.get("ZARINPAL_MERCHANT_CODE", ""),
            "SANDBOX": 1, 
        },
    },
    "IS_SAMPLE_FORM_ENABLE": True,  
    "DEFAULT": "ZARINPAL",
    "CURRENCY": "IRT",  
    "TRACKING_CODE_QUERY_PARAM": "tc",  
    "TRACKING_CODE_LENGTH": 16,  
    "SETTING_VALUE_READER_CLASS": "azbankgateways.readers.DefaultReader",  
    "BANK_PRIORITIES": [
    ], 
    "IS_SAFE_GET_GATEWAY_PAYMENT": True,  
    "CUSTOM_APP": None,  
}

CORS_ALLOW_ALL_ORIGINS = True

SMS_USERNAME  = os.getenv('SMS_USERNAME')
SMS_API_KEY = os.getenv('SMS_API_KEY')
SMS_LINE  = os.getenv('SMS_LINE')