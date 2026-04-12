"""
Django settings for Sangeet project.
"""

from pathlib import Path
from dotenv import load_dotenv
import os

# ================= BASE DIRECTORY =================
BASE_DIR = Path(__file__).resolve().parent.parent

# ================= LOAD .ENV FILE =================
dotenv_path = BASE_DIR / '.env'
load_dotenv(dotenv_path)

print(f"\n{'='*70}")
print(f"DEBUG: Loading environment variables")
print(f"BASE_DIR: {BASE_DIR}")
print(f"ENV Path: {dotenv_path}")
print(f"ENV Exists: {dotenv_path.exists()}")
print(f"{'='*70}\n")

# ================= SECURITY =================
SECRET_KEY = 'django-insecure-0#2iv0b(x%#lz9^o9svx&pc+3k9!thv=$ad+(x3bzcv-!)hz#-'

DEBUG = True

ALLOWED_HOSTS = ['*']


# ================= APPLICATIONS =================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'music',
]


# ================= MIDDLEWARE =================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# ================= URL CONFIG =================
ROOT_URLCONF = 'Sangeet.urls'


# ================= TEMPLATES =================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# ================= WSGI =================
WSGI_APPLICATION = 'Sangeet.wsgi.application'


# ================= DATABASE =================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# ================= PASSWORD VALIDATION =================
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


# ================= INTERNATIONALIZATION =================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# ================= STATIC FILES =================
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"


# ================= MEDIA FILES =================
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / "media"


# ================= DEFAULT PRIMARY KEY =================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ================= YOUTUBE CONFIGURATION =================
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

print(f"YouTube API Key: {YOUTUBE_API_KEY[:20]}..." if YOUTUBE_API_KEY else "❌ YouTube API Key not loaded")

X_FRAME_OPTIONS = 'ALLOW-FROM https://www.youtube.com'
SECURE_CROSS_ORIGIN_OPENER_POLICY = None

CSRF_TRUSTED_ORIGINS = [
    'https://www.youtube.com',
    'https://youtube.com',
    'https://www.youtube-nocookie.com',
]

CSP_FRAME_SRC = (
    "'self'",
    "https://www.youtube.com",
    "https://youtube.com",
    "https://www.youtube-nocookie.com",
)

SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = False


# ================= SPOTIFY CONFIGURATION =================
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

print(f"Spotify Client ID: {SPOTIFY_CLIENT_ID[:15]}..." if SPOTIFY_CLIENT_ID else "❌ Spotify Client ID not loaded")
print(f"Spotify Secret: {SPOTIFY_CLIENT_SECRET[:15]}..." if SPOTIFY_CLIENT_SECRET else "❌ Spotify Secret not loaded")

if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
    print(f"\n⚠️  WARNING: Spotify credentials not found!")
    print(f"   Make sure .env file is at: {BASE_DIR / '.env'}")
    print(f"   And contains SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET\n")
    
    
    
    
    
    
    
    
    
# ================= LASTFM CONFIGURATION =================
LASTFM_API_KEY = os.getenv("LASTFM_API_KEY")

print(f"\n{'='*70}")
print(f"LAST.FM CONFIGURATION")
print(f"Last.fm API Key loaded: {LASTFM_API_KEY is not None}")
if LASTFM_API_KEY:
    print(f"API Key: {LASTFM_API_KEY[:15]}...")
else:
    print(f"❌ WARNING: LASTFM_API_KEY not found in .env file")
print(f"{'='*70}\n")    
    