#!/usr/bin/env python
# encoding=utf-8
"""
Django settings for smart_QC project.

Generated by 'django-admin startproject' using Django 1.9.12.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '_4&g1d#@6w#zug*3-gw6emi!b5@b0my&+ovo4s$#g^zfq*g($x'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

SITE_ID = 1

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'xadmin',
    'crispy_forms',
    'reversion',
    'smart_QC.apps.website',
    'smart_QC.apps.test_api',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
]

ROOT_URLCONF = 'smart_QC.urls'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.i18n',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


WSGI_APPLICATION = 'smart_QC.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.9/topics/i18n/

FILE_CHARSET = 'utf-8'

DEFAULT_CHARSET = 'utf-8'

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

# TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# If you define a custom LANGUAGES setting, as explained in the previous bullet, you can mark the language names as
# translation strings – but use ugettext_lazy() instead of ugettext() to avoid a circular import.
from django.utils.translation import ugettext_lazy as _

LANGUAGES = [
    ('en', _('English')),
    ('zh-hans', _('Chinese')),
]

#  翻译文件所在目录，需要手工创建
# LOCALE_PATHS = [
#     os.path.join(os.path.dirname(BASE_DIR), 'locale').replace('\\', '/'),
# ]

# Settings for language cookie
# LANGUAGE_COOKIE_NAME = 'django_language'
# LANGUAGE_COOKIE_AGE = None
# LANGUAGE_COOKIE_DOMAIN = None
# LANGUAGE_COOKIE_PATH = '/'

DATETIME_FORMAT = 'Y-m-d H:i:s'  # suit在admin里设置时间的一个小bug。需要把时间格式指定一下
DATE_FORMAT = 'Y-m-d'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'smart_QC/smart_QC/static').replace('\\', '/')
STATIC_URL = '/static/'

STATICFILES_DIRS = []

MEDIA_URL = '/media/'

MEDIA_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'smart_QC/media').replace('\\', '/')
# email
EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'yourgmailaccount@gmail.com'
EMAIL_HOST_PASSWORD = 'yourgmailpassword'
#xadmin
# XADMIN_TITLE = 'Smart QC'
# XADMIN_FOOTER_TITLE = 'yuefan 2017'
# XADMIN_EXCLUDE_PLUGINS = []
# XADMIN_CONF = 'django_smart_QC.xadmin_conf'
# logging
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
            'level': 'DEBUG',
            'class': 'logging.StreamHandler'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        # 'django.db.backends': {
        #     'handlers': ['console'],
        #     'level': 'DEBUG',
        # }
    }
}

# 针对不同环境引入不同的配置
# from  settings_for_envs.dev import *