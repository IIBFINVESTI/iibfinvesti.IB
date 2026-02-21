from django.db import transaction
from .models import Investissement, HistoriqueGain

def distribuer_gains_quotidiens():
    # 1. On récupère les investissements actifs (On enlève le filtre derniere_maj_gain)
    investissements = Investissement.objects.filter(
        actif=True
    ).select_related('grille', 'utilisateur__profil')
    
    nombre_traite = 0
    
    with transaction.atomic():
        for inv in investissements:
            # 2. Calcul du gain
            montant_du_gain = (inv.grille.montant * inv.grille.pourcentage_gain) / 100
            
            # 3. Mise à jour du solde
            profil = inv.utilisateur.profil
            profil.solde += montant_du_gain
            profil.save()
            
            # 4. Création de l'historique
            HistoriqueGain.objects.create(
                profil=profil,
                montant=montant_du_gain,
                description=f"Gain journalier - Pack {inv.grille.nom}"
            )
            
            # Note : On ne touche pas à 'derniere_maj_gain' ici pour éviter l'erreur FieldError
            
            nombre_traite += 1
            
    if nombre_traite == 0:
        return "Aucun investissement actif trouvé."
    return f"Succès : {nombre_traite} gains distribués."