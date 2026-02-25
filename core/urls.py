from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

# ==============================================================================
# CONFIGURATION DES URLS RACINES (CORE) - VERSION MONETBIL
# ==============================================================================

urlpatterns = [
    # 1. INTERFACE D'ADMINISTRATION
    path('admin/', admin.site.urls),

    # 2. GESTION DES UTILISATEURS (Inscription, Connexion, Profils)
    path('users/', include('users.urls')), 

    # 3. SYSTÈME D'INVESTISSEMENT & PAIEMENTS (PONZI)
    # Inclut l'accueil, le dashboard et le WEBHOOK Monetbil à la racine
    path('', include('ponzi.urls')), 
]

# ==============================================================================
# GESTION DES FICHIERS STATIQUES ET MÉDIAS
# ==============================================================================

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # Configuration pour la production (PythonAnywhere)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# ==============================================================================
# RAPPEL DE CONFIGURATION MONETBIL
# ==============================================================================
# Ton URL de Webhook à renseigner chez Monetbil est : 
# https://iibfaraba.pythonanywhere.com/monetbil-webhook/