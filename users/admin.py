from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profil

# 1. Correction de l'erreur E202 : On précise fk_name='user'
class ProfilInline(admin.StackedInline):
    model = Profil
    fk_name = 'user'  # <-- CETTE LIGNE EST INDISPENSABLE
    can_delete = False
    verbose_name_plural = 'Configuration IIBF (Solde, Packs, Parrainage)'
    fields = (
        'telephone', 
        'solde', 
        'parrain', 
        'pack_nom', 
        'pack_montant', 
        'pourcentage_journalier', 
        'derniere_maj_gain',
        'commission_payee'
    )

# 2. Amélioration de la liste principale des Utilisateurs
class UserAdmin(BaseUserAdmin):
    inlines = (ProfilInline,)
    
    list_display = ('username', 'get_telephone', 'get_solde', 'get_pack', 'get_parrain', 'is_staff')
    list_filter = ('is_staff', 'is_active', 'profil__pack_nom')

    def get_telephone(self, instance):
        # Utilisation de getattr pour éviter les erreurs si le profil n'existe pas
        return getattr(instance.profil, 'telephone', '')
    get_telephone.short_description = 'Téléphone'

    def get_solde(self, instance):
        return f"{getattr(instance.profil, 'solde', 0)} FCFA"
    get_solde.short_description = 'Solde'

    def get_pack(self, instance):
        pack = getattr(instance.profil, 'pack_nom', None)
        return pack if pack else "Aucun"
    get_pack.short_description = 'Pack Actif'

    def get_parrain(self, instance):
        return getattr(instance.profil, 'parrain', "Aucun")
    get_parrain.short_description = 'Parrain'

# Ré-enregistrement de User
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# 3. Menu "Profils" séparé (Vue Expert)
@admin.register(Profil)
class ProfilAdmin(admin.ModelAdmin):
    list_display = (
        'user', 
        'solde', 
        'pack_nom', 
        'pack_montant', 
        'pourcentage_journalier', 
        'telephone', 
        'parrain'
    )
    
    # Édition rapide depuis la liste
    list_editable = ('solde', 'pack_nom', 'pack_montant', 'pourcentage_journalier') 
    search_fields = ('user__username', 'telephone', 'parrain__username', 'pack_nom')
    list_filter = ('pack_nom', 'parrain', 'derniere_maj_gain')
    readonly_fields = ('date_creation',)