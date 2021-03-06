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

# SECURITY WARNING: don't running with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

SITE_ID = 1

# django-celery config
import djcelery
djcelery.setup_loader()
# Celery settings
BROKER_URL = 'redis://127.0.0.1:6379'               # 指定 Broker
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'  # 指定 Backend
#: Only add pickle to this list if your broker is secured
#: from unwanted access (see userguide/security.html)
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
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
    'djcelery',
    # 'kombu.transport.django',  # 基于Django的broker
    'smart_QC.apps.task',
    'sortedm2m',
    'multiselectfield',
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
        'DIRS': [os.path.join(BASE_DIR, 'smart_QC/templates'.replace('\\', '/'))],
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
STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'smart_QC/staticfiles/').replace('\\', '/')
STATIC_URL = '/static/'

STATICFILES_DIRS = [os.path.join(os.path.dirname(BASE_DIR), 'smart_QC/smart_QC/static').replace('\\', '/'),
                    ]

MEDIA_URL = '/media/'

MEDIA_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'smart_QC/media').replace('\\', '/')

#xadmin
# XADMIN_TITLE = 'Smart QC'
# XADMIN_FOOTER_TITLE = 'yuefan 2017'
# XADMIN_EXCLUDE_PLUGINS = []
# XADMIN_CONF = 'django_smart_QC.xadmin_conf'

CELERY_TIMEZONE = TIME_ZONE

# CELERY_ALWAYS_EAGER = True
CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'

# smart qc model constant
EVAL_SAFE_MODULES = (
    ('random', 'random'),
    ('time', 'time'),
    ('date', 'date'),
    ('datetime', 'datetime'),
    ('assertpy', 'assertpy')
)
SMARTQC_REPORT_TITLE = "Http Api Test"
SMARTQC_REPORT_DISCRIPTION = "Report output by Smart QC"
SMARTQC_FAILURE_EXCEPTION = AssertionError  # determines which exception will be raised when the instance's assertion methods fail; test methods raising this exception will be deemed to have 'failed' rather than 'errored'.
# 管理员邮箱
ADMINS = (
    ('laixintao', '*******@163.com'),
)

# 非空链接，却发生404错误，发送通知MANAGERS
SEND_BROKEN_LINK_EMAILS = True
MANAGERS = ADMINS

# Email设置
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.163.com'  # QQ邮箱SMTP服务器(邮箱需要开通SMTP服务)
EMAIL_PORT = 25  # QQ邮箱SMTP服务端口
EMAIL_HOST_USER = '**********@163.com'  # 我的邮箱帐号
EMAIL_HOST_PASSWORD = '**************'  # 授权码
EMAIL_SUBJECT_PREFIX = 'website'  # 为邮件标题的前缀,默认是'[django]'
EMAIL_USE_TLS = True  # 开启安全链接
DEFAULT_FROM_EMAIL = SERVER_EMAIL = EMAIL_HOST_USER  # 设置发件人

# logging日志配置
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {  # 日志格式
        'standard': {
            'format': '%(asctime)s [%(threadName)s:%(thread)d] [%(name)s:%(lineno)d] [%(module)s:%(funcName)s] [%(levelname)s]- %(message)s'}
    },
    'filters': {  # 过滤器
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        }
    },
    'handlers': {  # 处理器
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'mail_admins': {  # 发送邮件通知管理员
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false'],  # 仅当 DEBUG = False 时才发送邮件
            'include_html': True,
        },
        'default': {  # 记录到日志文件(需要创建对应的目录，否则会出错)
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, "log", 'debug.log'),  # 日志输出文件
            'maxBytes': 1024 * 1024 * 5,  # 文件大小
            'backupCount': 5,  # 备份份数
            'formatter': 'standard',  # 使用哪种formatters日志格式
        },
        'console': {  # 输出到控制台
            # 'level': 'DEBUG',
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
    },
    'loggers': {  # logging管理器
        'django': {
            'handlers': ['default', 'console'],
            'level': 'DEBUG',
            'propagate': False
        },
        'django.request': {
            'handlers': ['default', 'mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        # 对于不在 ALLOWED_HOSTS 中的请求不发送报错邮件
        'django.security.DisallowedHost': {
            'handlers': ['null'],
            'propagate': False,
        },
        'smart_QC': {
            'handlers': ['default', 'console', 'mail_admins'],
            'level': 'INFO',
            # 'filters': ['special']
        }
    }
}

# 针对不同环境引入不同的配置
# from  settings_for_envs.dev import *