from django.urls import path
from . import views

urlpatterns = [
    # --- Authentification ---
    path('inscription/', views.inscription_view, name='inscription'),
    path('connexion/', views.connexion_view, name='connexion'),
    path('deconnexion/', views.deconnexion_view, name='deconnexion'),

    # --- Interface Principale ---
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # --- Système d'Investissement ---
    # Pour déduire du solde
    path('activer-pack/<int:grille_id>/', views.valider_investissement, name='activer_pack'),
    
    # Pour rediriger vers WhatsApp
    path('contact-whatsapp/<int:grille_id>/', views.investir_maintenant, name='investir_maintenant'),
    
    # --- Onglet Marchés (CORRIGÉ ICI) ---
    # On pointe vers la vue qui liste les packs (catalogue_packs_view)
    path('marches/', views.catalogue_packs_view, name='packs'),
]