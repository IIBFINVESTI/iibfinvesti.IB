from django.urls import path
from . import views

urlpatterns = [
    # --- 1. Accueil & Landing Page ---
    path('', views.index_view, name='index'), 
    
    # --- 2. Espace Personnel (Le Dashboard) ---
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # --- 3. Le Marché (Catalogue des Packs) ---
    path('marches/', views.liste_packs, name='packs'),
    
    # --- 4. Gestion des Transactions (Retraits) ---
    path('retrait/', views.demander_retrait, name='demander_retrait'),
    
    # --- 5. Actions d'Investissement ---
    path('activer-pack/<int:grille_id>/', views.activer_pack, name='activer_pack'),

    # --- 6. Outils Système & Maintenance ---
    # J'ai gardé le nom 'simuler_gains' que tu avais, 
    # MAIS j'ai ajouté 'simuler_gains_test' au cas où ton template l'appelle ainsi.
    path('simuler-gains/', views.simuler_gains_test, name='simuler_gains_test'),
]