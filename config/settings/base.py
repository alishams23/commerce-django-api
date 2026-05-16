from datetime import timedelta
import os
from django.utils.translation import gettext_lazy as _

from config.settings import BASE_DIR


AUTH_USER_MODEL = "user.User"

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
]

# TODO: Add your apps here. (PROJECT_NAME)_APPS = ['your_app_name']
PROJECT_NAME_APPS = [
    "blog",
    "product",
    "user",
    "order",
    "helpdesk",
    "payments",
    "promotions",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework.authtoken",
    "rest_framework_simplejwt.token_blacklist",
    "django_filters",
    "django_ckeditor_5",
    "dj_rest_auth",
    "drf_spectacular",
    "colorfield",
    "corsheaders",
    "azbankgateways",
]

INSTALLED_APPS = DJANGO_APPS + PROJECT_NAME_APPS + THIRD_PARTY_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


ROOT_URLCONF = "config.urls"

WSGI_APPLICATION = "config.wsgi.application"


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / 'templates'],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",  # postgresql_psycopg2
        "NAME": os.environ.get("POSTGRES_DB"),
        "USER": os.environ.get("POSTGRES_USER"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD"),
        "HOST": os.environ.get("POSTGRES_HOST"),
        "PORT": os.environ.get("POSTGRES_PORT"),
    }
}


REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        # 'rest_framework.authentication.BasicAuthentication',
        # 'rest_framework.authentication.SessionAuthentication',
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

REST_AUTH = {
    "USE_JWT": True,
    # "JWT_AUTH_RETURN_EXPIRATION": True,
    "JWT_AUTH_HTTPONLY": False,
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),   
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7), 
    'BLACKLIST_AFTER_ROTATION': True,
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LOCALE_PATHS = [
    BASE_DIR / "locale",
]

LANGUAGES = (
    ("fa", _("Persian")),
    ("en", _("English")),
)

LANGUAGE_CODE = "fa-ir"

TIME_ZONE = "Asia/Tehran"

USE_I18N = True

USE_L10N = True

USE_TZ = True
STATIC_URL = "/static/"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_ROOT = os.path.join(BASE_DIR, 'media/') # 'media' is my media folder
MEDIA_URL = '/media/'

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


def env_bool(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}

# celery
CELERY_BROKER_URL = f"redis://{os.environ.get('REDIS_HOST')}:{os.environ.get('REDIS_PORT')}/0"
CELERY_RESULT_BACKEND = f"redis://{os.environ.get('REDIS_HOST')}:{os.environ.get('REDIS_PORT')}/0"
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

SESSION_COOKIE_SECURE = env_bool("DJANGO_SECURE_COOKIES", default=False)
CSRF_COOKIE_SECURE = env_bool("DJANGO_SECURE_COOKIES", default=False)

APPEND_SLASH = False

CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': [
            'heading', '|',
            'bold', 'italic', 'underline', '|',
            'fontSize', '|',
            'fontColor', 'fontBackgroundColor', '|',
            'alignment', 'outdent', 'indent', '|',
            'bulletedList', 'numberedList', '|',
            'link', 'imageUpload', 'insertTable', '|',
            'undo', 'redo'
        ],
        'height': 300,
        'width': 'auto',
        'language': 'fa',
        'fontSize': {
            'options': [10, 12, 14, 16, 'default', 18, 20, 24],
        },
        'extraAllowedContent': '*{color}',
        'contentCss': [
            'body { color: black; }'
        ],
        'image': {
            'upload': {
                'types': ['jpeg', 'png', 'gif', 'bmp', 'webp'],
                'directory': 'blog/content/%Y/%m/'
            }
        }
    },
}