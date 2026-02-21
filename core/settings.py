import os
from pathlib import Path

# 1. Chemin de base
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-iibf-plateforme-cle-privee-2026'

DEBUG = True

# AJUSTEMENT : On liste explicitement ton domaine ngrok
ALLOWED_HOSTS = ['*', 'frontierless-chalky-keturah.ngrok-free.dev']

# --- CONFIGURATION CSRF & SESSIONS POUR NGROK ---
CSRF_TRUSTED_ORIGINS = [
    'https://frontierless-chalky-keturah.ngrok-free.dev'
]

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
# ----------------------------------------------

# 2. Définition des Applications
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    'django_q', # Automatisation des gains

    'users.apps.UsersConfig',
    'ponzi', 
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

# 3. Configuration des Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
            BASE_DIR / 'ponzi' / 'templates',
        ], 
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# 4. Base de données (CORRECTION POUR DATABASE IS LOCKED)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'OPTIONS': {
            'timeout': 20,  # Augmente l'attente à 20 secondes pour éviter les blocages
        },
    }
}

# 5. Django Q2 (Moteur de tâches IIBF)
Q_CLUSTER = {
    'name': 'IIBF_Tasks',
    'workers': 2,
    'recycle': 500,
    'timeout': 60,
    'compress': True,
    'save_limit': 250,
    'queue_limit': 500,
    'label': 'Django Q Admin',
    'orm': 'default',
}

# 6. Validation des mots de passe
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': { 'min_length': 6 }
    },
]

# 7. Internationalisation
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Douala'
USE_I18N = True
USE_TZ = True

# 8. Fichiers Statiques
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static'] if (BASE_DIR / 'static').exists() else []
STATIC_ROOT = BASE_DIR / 'staticfiles'

# 9. Redirections d'Authentification
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'connexion'
LOGIN_URL = 'connexion'

# 10. Type par défaut
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'