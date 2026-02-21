from django.contrib import admin
from .models import Grille, Investissement, HistoriqueGain, Retrait, Configuration

@admin.register(Configuration)
class ConfigurationAdmin(admin.ModelAdmin):
    list_display = ('nom_site', 'pourcentage_parrainage')

@admin.register(Grille)
class GrilleAdmin(admin.ModelAdmin):
    list_display = ('nom', 'montant', 'pourcentage_gain', 'duree_jours')

@admin.register(Investissement)
class InvestissementAdmin(admin.ModelAdmin):
    # 'utilisateur' existe dans le modèle, mais 'total_cumule' n'existe pas, donc on l'enlève
    list_display = ('utilisateur', 'grille', 'date_activation', 'actif')
    list_filter = ('actif', 'grille')

@admin.register(HistoriqueGain)
class HistoriqueGainAdmin(admin.ModelAdmin):
    # Ici, on remplace 'utilisateur' par 'get_user' car le champ s'appelle 'profil' maintenant
    list_display = ('get_user', 'montant', 'date_distribution', 'description')
    
    def get_user(self, obj):
        return obj.profil.user.username
    get_user.short_description = 'Utilisateur'

@admin.register(Retrait)
class RetraitAdmin(admin.ModelAdmin):
    list_display = ('get_user', 'montant', 'numero_paiement', 'statut', 'date_demande')
    list_editable = ('statut',) # Pour valider les retraits en un clic
    list_filter = ('statut', 'date_demande')

    def get_user(self, obj):
        return obj.profil.user.username
    get_user.short_description = 'Utilisateur'