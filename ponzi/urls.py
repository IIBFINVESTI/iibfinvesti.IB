from django.urls import path
from . import views

urlpatterns = [
    # --- 1. ACCUEIL & LANDING PAGE ---
    # Affiche la page d'entrée du site
    path('', views.index_view, name='index'), 
    
    # --- 2. ESPACE PERSONNEL (DASHBOARD) ---
    # Le cœur de l'application pour l'utilisateur connecté
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # --- 3. LE MARCHÉ (CATALOGUE DES PACKS) ---
    # Liste tous les packs d'investissement disponibles
    path('marches/', views.liste_packs, name='packs'),

    # --- 4. INTERFACE DE DÉPÔT LIBRE ---
    # La page avec les logos Orange/MTN pour recharger le solde
    path('depot/', views.initier_depot, name='depot'),
    
    # --- 5. GESTION DES FLUX FINANCIERS (RETRAITS) ---
    # Formulaire pour retirer de l'argent le samedi soir
    path('retrait/', views.demander_retrait, name='demander_retrait'),

    # --- 6. SYSTÈME DE PAIEMENT MONETBIL ---
    # Envoie l'utilisateur vers le widget de paiement
    path('initier-paiement/', views.initier_paiement, name='initier-paiement'),

    # URL invisible appelée par Monetbil pour confirmer la réception de l'argent
    path('monetbil-webhook/', views.monetbil_webhook, name='monetbil-webhook'),
]