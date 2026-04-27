import os
from datetime import timedelta

from .base import *

DEBUG = os.environ.get("DEBUG")

ALLOWED_HOSTS = ['*']



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
