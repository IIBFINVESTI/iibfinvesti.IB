from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .models import Grille, Investissement, HistoriqueGain, Retrait
from django.utils import timezone # Meilleur pour la gestion Africa/Douala
from decimal import Decimal, InvalidOperation
from .utils import distribuer_gains_quotidiens 

# 1. Page d'accueil publique
def index_view(request):
    return render(request, 'ponzi/index.html')

# 2. Dashboard de l'utilisateur
@login_required
def dashboard_view(request):
    profil = request.user.profil
    # Récupération des investissements actifs
    mes_investissements = Investissement.objects.filter(utilisateur=request.user, actif=True)
    # Historique des 7 derniers gains
    derniers_gains = HistoriqueGain.objects.filter(profil=profil).order_by('-date_distribution')[:7]
    
    # Logique du retrait (Samedi 18h)
    maintenant = timezone.now()
    est_samedi = maintenant.weekday() == 5
    heure_valide = maintenant.hour >= 18
    peut_retirer = est_samedi and heure_valide

    context = {
        'profil': profil,
        'mes_investissements': mes_investissements,
        'derniers_gains': derniers_gains,
        'peut_retirer': peut_retirer,
    }
    return render(request, 'ponzi/dashboard.html', context)

# 3. LE MARCHÉ (La fonction qui manquait pour vos URLs)
@login_required
def liste_packs(request):
    """Affiche tous les packs disponibles à l'achat"""
    grilles = Grille.objects.all().order_by('montant')
    return render(request, 'ponzi/marches.html', {'grilles': grilles})

# 4. Activer un pack d'investissement
@login_required
def activer_pack(request, grille_id):
    if request.method != 'POST':
        return redirect('packs')
        
    grille = get_object_or_404(Grille, id=grille_id)
    profil = request.user.profil

    if profil.solde < grille.montant:
        messages.error(request, f"Solde insuffisant ! Il vous manque {grille.montant - profil.solde} FCFA.")
        return redirect('packs')

    try:
        with transaction.atomic():
            # Déduction du solde
            profil.solde -= grille.montant
            profil.save()

            # Création de l'investissement
            Investissement.objects.create(
                utilisateur=request.user,
                grille=grille,
                actif=True
            )
            
        messages.success(request, f"Félicitations ! Votre pack {grille.nom} est maintenant actif.")
    except Exception as e:
        messages.error(request, "Une erreur technique est survenue.")
        
    return redirect('dashboard')

# 5. Demande de retrait
@login_required
def demander_retrait(request):
    profil = request.user.profil
    maintenant = timezone.now()
    
    # Restriction (à commenter pour tes tests)
    if not (maintenant.weekday() == 5 and maintenant.hour >= 18):
        messages.warning(request, "Les retraits ne sont ouverts que le samedi à partir de 18h.")
        return redirect('dashboard')

    if request.method == 'POST':
        try:
            montant = Decimal(request.POST.get('montant', '0').replace(',', '.'))
            numero = request.POST.get('telephone')

            if montant < 1000:
                messages.error(request, "Minimum 1000 FCFA.")
            elif montant > profil.solde:
                messages.error(request, "Solde insuffisant.")
            elif not numero or len(numero) < 8:
                messages.error(request, "Numéro invalide.")
            else:
                with transaction.atomic():
                    profil.solde -= montant
                    profil.save()
                    Retrait.objects.create(
                        profil=profil, montant=montant, 
                        numero_paiement=numero, statut='EN_ATTENTE'
                    )
                messages.success(request, "Demande envoyée !")
                return redirect('dashboard')
        except (InvalidOperation, ValueError):
            messages.error(request, "Montant invalide.")

    return render(request, 'ponzi/retrait.html', {'profil': profil})

# 6. Simulation manuelle (Admin)
@login_required
def simuler_gains_test(request):
    if not request.user.is_staff:
        messages.error(request, "Accès réservé.")
        return redirect('dashboard')
    
    resultat = distribuer_gains_quotidiens()
    messages.success(request, resultat)
    return redirect('dashboard')