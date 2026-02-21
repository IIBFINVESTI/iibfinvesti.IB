from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from decimal import Decimal
from django.utils import timezone

# --- Modèle Profil ---

class Profil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profil')
    telephone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Numéro de téléphone")
    solde = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name="Solde du compte")
    
    pack_nom = models.CharField(max_length=100, null=True, blank=True, verbose_name="Pack Actuel")
    pack_montant = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name="Montant Investi")
    pourcentage_journalier = models.FloatField(default=0.0, verbose_name="% Journalier")
    derniere_maj_gain = models.DateField(null=True, blank=True, verbose_name="Date du dernier gain versé")

    parrain = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='filleuls', verbose_name="Parrain")
    commission_payee = models.BooleanField(default=False, verbose_name="Commission de parrainage versée ?")
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date d'inscription")

    class Meta:
        verbose_name = "Profil"
        verbose_name_plural = "Profils"

    def __str__(self):
        return f"Profil de {self.user.username} ({self.solde} FCFA)"


# --- Modèle Grille ---

class Grille(models.Model):
    nom = models.CharField(max_length=100, verbose_name="Nom du Pack")
    montant = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Prix (FCFA)")
    pourcentage_gain = models.FloatField(verbose_name="% Gain Journalier")

    class Meta:
        verbose_name = "Catalogue Pack"
        verbose_name_plural = "Catalogue Packs"

    def __str__(self):
        return f"{self.nom} - {self.montant} FCFA"


# --- Modèle Investissement ---

class Investissement(models.Model):
    profil = models.ForeignKey(Profil, on_delete=models.CASCADE, related_name='investissements')
    pack = models.ForeignKey(Grille, on_delete=models.PROTECT)
    date_activation = models.DateTimeField(auto_now_add=True)
    actif = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Investissement Actif"
        verbose_name_plural = "Investissements Actifs"

    def __str__(self):
        return f"{self.profil.user.username} - {self.pack.nom}"


# --- NOUVEAU: Modèle HistoriqueGain (Indispensable pour tes vues) ---

class HistoriqueGain(models.Model):
    profil = models.ForeignKey(Profil, on_delete=models.CASCADE, related_name='historique_gains')
    montant = models.DecimalField(max_digits=12, decimal_places=2)
    date_distribution = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255, default="Gain journalier")

    class Meta:
        verbose_name = "Historique des Gains"
        verbose_name_plural = "Historique des Gains"


# --- Signaux ---

@receiver(post_save, sender=User)
def create_user_profil(sender, instance, created, **kwargs):
    if created:
        Profil.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_profil(sender, instance, **kwargs):
    if hasattr(instance, 'profil'):
        instance.profil.save()

@receiver(pre_save, sender=Profil)
def commission_premier_depot(sender, instance, **kwargs):
    if instance.pk: 
        try:
            ancien_profil = Profil.objects.get(pk=instance.pk)
            if instance.solde > ancien_profil.solde and not instance.commission_payee and instance.parrain:
                montant_depose = instance.solde - ancien_profil.solde
                commission = montant_depose * Decimal('0.05')
                parrain_profil = instance.parrain.profil
                parrain_profil.solde += commission
                parrain_profil.save()
                instance.commission_payee = True
        except Profil.DoesNotExist:
            pass