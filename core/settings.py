import os
from pathlib import Path

# ==============================================================================
# 1. CHEMINS ET CONFIGURATION DE BASE
# ==============================================================================
BASE_DIR = Path(__file__).resolve().parent.parent

# UTILISATION DE VARIABLES D'ENVIRONNEMENT POUR LA SÉCURITÉ
# En production, définissez DJANGO_SECRET_KEY dans votre console PythonAnywhere
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-iibf-plateforme-cle-privee-2026')

# DEBUG à False pour la production
DEBUG = os.getenv('DJANGO_DEBUG', 'False') == 'True'

# Configuration des hôtes autorisés
ALLOWED_HOSTS = [
    'iibfaraba.pythonanywhere.com', 
    'localhost', 
    '127.0.0.1', 
    '.ngrok-free.dev',
    'frontierless-chalky-keturah.ngrok-free.dev'
]

# ==============================================================================
# 2. SÉCURITÉ (CSRF, SESSIONS & SSL)
# ==============================================================================
CSRF_TRUSTED_ORIGINS = [
    'https://frontierless-chalky-keturah.ngrok-free.dev',
    'https://iibfaraba.pythonanywhere.com'
]

# Configuration spécifique pour le proxy inverse de PythonAnywhere
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Empêche l'inclusion du site dans une iframe (protection contre le Clickjacking)
X_FRAME_OPTIONS = 'DENY'

# ==============================================================================
# 3. DÉFINITION DES APPLICATIONS
# ==============================================================================
INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Automatisation des tâches
    'django_q', 

    # Applications locales
    'users.apps.UsersConfig',
    'ponzi', 
]

# ==============================================================================
# 4. MIDDLEWARES
# ==============================================================================
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

# ==============================================================================
# 5. CONFIGURATION DES TEMPLATES
# ==============================================================================
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

# ==============================================================================
# 6. BASE DE DONNÉES
# ==============================================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'OPTIONS': {
            'timeout': 20, # Crucial pour éviter les "Database is locked" sur SQLite
        },
    }
}

# ==============================================================================
# 7. DJANGO Q2 (CLUSTER)
# ==============================================================================
# Rappel : Sur PythonAnywhere, lancez "python manage.py qcluster" dans une console dédiée
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

# ==============================================================================
# 8. AUTHENTIFICATION & MOTS DE PASSE
# ==============================================================================
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': { 'min_length': 6 }
    },
]

# Redirections
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'connexion'
LOGIN_URL = 'connexion'

# ==============================================================================
# 9. INTERNATIONALISATION (FRANCE / CAMEROUN)
# ==============================================================================
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Douala'
USE_I18N = True
USE_TZ = True

# ==============================================================================
# 10. FICHIERS STATIQUES ET MÉDIAS
# ==============================================================================
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static', # On force la lecture du dossier static
]
STATIC_ROOT = BASE_DIR / 'staticfiles'
# Configuration pour les fichiers uploadés par les utilisateurs (si nécessaire)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==============================================================================
## ==============================================================================
# 11. CONFIGURATION MONETBIL (SÉCURISÉE)
# ==============================================================================
# On récupère les clés depuis l'environnement du serveur
MONETBIL_SERVICE_KEY = os.getenv('MONETBIL_SERVICE_KEY')
MONETBIL_SERVICE_SECRET = os.getenv('MONETBIL_SERVICE_SECRET')
MONETBIL_WIDGET_URL = "https://www.monetbil.com/pay/v2.1/"

# Vérification de sécurité pour éviter que le site crash si les clés sont oubliées
if not MONETBIL_SERVICE_KEY:
    print("⚠️ WARNING: MONETBIL_SERVICE_KEY non configurée dans l'environnement !")
# ==============================================================================
# CONFIGURATION JAZZMIN (INTERFACE ADMIN PREMIUM)
# ==============================================================================
JAZZMIN_SETTINGS = {
    "site_title": "IIBF ADMIN",
    "site_header": "IIBF ADMINISTRATEUR", 
    "site_brand": "IIBF TECHNOLOGY", 
    "welcome_sign": "CENTRE DE CONTRÔLE IIBF - ACCÈS ADMINISTRATEUR", 
    "copyright": "IIBF Group Ltd",
    "search_model": ["auth.User", "users.Profil"],
    "show_sidebar": True,
    "navigation_expanded": True,
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user-shield",
        "users.Profil": "fas fa-id-card",
        "ponzi.Grille": "fas fa-layer-group",
        "ponzi.Investissement": "fas fa-chart-line",
        "ponzi.Retrait": "fas fa-money-bill-wave",
        "ponzi.Configuration": "fas fa-tools",
        "ponzi.HistoriqueGain": "fas fa-history",
    },
    "order_with_respect_to": ["ponzi", "users", "auth"], 
    "theme": "darkly", 
    "dark_mode_theme": "darkly",
}
JAZZMIN_SETTINGS = {
    "site_title": "IIBF ADMIN",
    "site_header": "IIBF ADMINISTRATEUR", 
    "site_brand": "IIBF TECHNOLOGY", 
    "welcome_sign": "CENTRE DE CONTRÔLE IIBF - ACCÈS ADMINISTRATEUR", 
    "copyright": "IIBF Group Ltd",
    "search_model": ["auth.User", "users.Profil"],
    "show_sidebar": True,
    "navigation_expanded": True,
    "show_ui_builder": True, # Pour personnaliser l'interface en direct
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user-shield",
        "users.Profil": "fas fa-id-card",
        "ponzi.Grille": "fas fa-layer-group",
        "ponzi.Investissement": "fas fa-chart-line",
        "ponzi.Retrait": "fas fa-money-bill-wave",
        "ponzi.Configuration": "fas fa-tools",
        "ponzi.HistoriqueGain": "fas fa-history",
    },
    "order_with_respect_to": ["ponzi", "users", "auth"], 
    "theme": "darkly", 
    "dark_mode_theme": "darkly",
    "custom_css": "css/admin_custom.css",
}