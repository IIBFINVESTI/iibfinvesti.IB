from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.dispatch import receiver
from decimal import Decimal
from users.models import Profil  # Liaison avec l'application users

# --- CONFIGURATION DYNAMIQUE ---
class Configuration(models.Model):
    nom_site = models.CharField(max_length=100, default="IIBF INVEST")
    pourcentage_parrainage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=5.00, 
        help_text="En pourcentage (ex: 5.00 pour 5%)"
    )

    class Meta:
        verbose_name = "Configuration Générale"
        verbose_name_plural = "Configuration Générale"

    def __str__(self):
        return self.nom_site

# --- GRILLES D'INVESTISSEMENT ---
class Grille(models.Model):
    nom = models.CharField(max_length=100)
    montant = models.DecimalField(max_digits=12, decimal_places=2)
    pourcentage_gain = models.DecimalField(max_digits=5, decimal_places=2)
    duree_jours = models.IntegerField(default=30)

    def __str__(self):
        return f"{self.nom} ({self.montant} FCFA)"

# --- INVESTISSEMENTS ACTIFS ---
class Investissement(models.Model):
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    grille = models.ForeignKey(Grille, on_delete=models.CASCADE)
    date_activation = models.DateTimeField(auto_now_add=True)
    actif = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.utilisateur.username} - {self.grille.nom}"

# --- HISTORIQUE DES GAINS ---
class HistoriqueGain(models.Model):
    # CHANGEMENT ICI : related_name unique pour l'app ponzi
    profil = models.ForeignKey(Profil, on_delete=models.CASCADE, related_name='historique_gains_ponzi')
    montant = models.DecimalField(max_digits=12, decimal_places=2)
    date_distribution = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255, default="Gain journalier")

    def __str__(self):
        return f"{self.profil.user.username} : +{self.montant} FCFA"

# --- RETRAITS ---
class Retrait(models.Model):
    STATUTS = [
        ('EN_ATTENTE', 'En attente'), 
        ('VALIDE', 'Validé'), 
        ('REJETE', 'Rejeté')
    ]
    # CHANGEMENT ICI : related_name unique pour l'app ponzi
    profil = models.ForeignKey(Profil, on_delete=models.CASCADE, related_name='retraits_ponzi')
    montant = models.DecimalField(max_digits=12, decimal_places=2)
    numero_paiement = models.CharField(max_length=25)
    statut = models.CharField(max_length=20, choices=STATUTS, default='EN_ATTENTE')
    date_demande = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Retrait de {self.montant} par {self.profil.user.username}"


# --- SIGNAL : COMMISSION DE PARRAINAGE ---
@receiver(pre_save, sender=Profil)
def commission_premier_depot(sender, instance, **kwargs):
    if instance.pk:
        try:
            ancien_profil = Profil.objects.get(pk=instance.pk)
            
            if instance.solde > ancien_profil.solde and not instance.commission_payee and instance.parrain:
                config = Configuration.objects.first()
                pourcentage = config.pourcentage_parrainage if config else Decimal('5.00')
                
                montant_depose = instance.solde - ancien_profil.solde
                commission = (montant_depose * pourcentage) / 100
                
                parrain_profil = instance.parrain.profil
                parrain_profil.solde += commission
                parrain_profil.save()
                
                HistoriqueGain.objects.create(
                    profil=parrain_profil,
                    montant=commission,
                    description=f"Bonus parrainage ({pourcentage}%) sur dépôt de {instance.user.username}"
                )
                
                instance.commission_payee = True
                
        except Profil.DoesNotExist:
            pass
        except Exception as e:
            print(f"Erreur lors du calcul de commission: {e}")