import uuid
import logging
from decimal import Decimal, InvalidOperation

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User

# Importation de tes modèles et utilitaires
from .models import Grille, Investissement, HistoriqueGain, Retrait
from .utils import distribuer_gains_quotidiens 

# Configuration du logger pour le suivi des transactions
logger = logging.getLogger(__name__)

# ==============================================================================
# 1. PAGES PUBLIQUES & DASHBOARD
# ==============================================================================

def index_view(request):
    """Page d'accueil du site."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'ponzi/index.html')

@login_required
def dashboard_view(request):
    """Tableau de bord principal de l'investisseur."""
    profil = request.user.profil
    
    # Récupération des investissements actifs
    mes_investissements = Investissement.objects.filter(
        utilisateur=request.user, 
        actif=True
    ).select_related('grille')
    
    # Historique des derniers gains
    derniers_gains = HistoriqueGain.objects.filter(profil=profil).order_by('-date_distribution')[:7]
    
    # Vérification de l'ouverture des retraits (Samedi 18h)
    maintenant = timezone.now()
    peut_retirer = (maintenant.weekday() == 5 and maintenant.hour >= 18)

    context = {
        'profil': profil,
        'mes_investissements': mes_investissements,
        'derniers_gains': derniers_gains,
        'peut_retirer': peut_retirer,
        'grilles': Grille.objects.all().order_by('montant'),
    }
    return render(request, 'ponzi/dashboard.html', context)

# ==============================================================================
# 1.1 FONCTIONS AJOUTÉES (POUR CORRIGER LES ERREURS URLS)
# ==============================================================================

@login_required
def liste_packs(request):
    """Affiche le catalogue des packs d'investissement."""
    grilles = Grille.objects.all().order_by('montant')
    return render(request, 'ponzi/marches.html', {'grilles': grilles})

@login_required
def simuler_gains_test(request):
    """Force la distribution des gains (Utile pour tes tests en local)."""
    distribuer_gains_quotidiens()
    messages.success(request, "💸 Simulation des gains réussie !")
    return redirect('dashboard')

@login_required
def initier_depot(request):
    """Affiche la page de choix du montant de dépôt (Logos Orange/MTN)."""
    return render(request, 'ponzi/depot.html')

# ==============================================================================
# 2. FLUX DE PAIEMENT (MONETBIL)
# ==============================================================================

@login_required
def initier_paiement(request):
    """Prépare la transaction et redirige vers Monetbil."""
    if request.method == "POST":
        montant = request.POST.get('amount')
        grille_id = request.POST.get('grille_id', 'SOLDE') 
        
        if not montant:
            messages.error(request, "Veuillez entrer un montant valide.")
            return redirect('dashboard')

        ref_combinee = f"{request.user.id}|{grille_id}"

        params = {
            'service': settings.MONETBIL_SERVICE_KEY,
            'amount': montant,
            'currency': 'XAF',
            'item_ref': ref_combinee, 
            'order_id': f"INV-{uuid.uuid4().hex[:6].upper()}",
            'email': request.user.email,
            'return_url': request.build_absolute_uri('/dashboard/'),
            'notify_url': 'https://iibfaraba.pythonanywhere.com/monetbil-webhook/', 
        }
        
        from urllib.parse import urlencode
        query_string = urlencode(params)
        pay_url = f"{settings.MONETBIL_WIDGET_URL}{settings.MONETBIL_SERVICE_KEY}?{query_string}"
        
        return redirect(pay_url)

    return redirect('dashboard')

@csrf_exempt
def monetbil_webhook(request):
    """Validation automatique du paiement par le serveur Monetbil."""
    data = request.POST if request.method == 'POST' else request.GET
    status = data.get('status')
    ref_combinee = data.get('item_ref') 

    if status == 'success' and ref_combinee:
        try:
            user_id, action_id = ref_combinee.split('|')
            montant_final = Decimal(data.get('amount', 0))
            
            with transaction.atomic():
                user = User.objects.get(id=user_id)
                
                if action_id == "SOLDE":
                    user.profil.solde += montant_final
                    user.profil.save()
                    logger.info(f"💰 DEPÔT REUSSI : {user.username}")
                else:
                    grille = Grille.objects.get(id=action_id)
                    Investissement.objects.create(
                        utilisateur=user,
                        grille=grille,
                        actif=True,
                        date_activation=timezone.now()
                    )
                    logger.info(f"✅ PACK ACTIVE : {grille.nom} pour {user.username}")
                
            return HttpResponse("SUCCESS", status=200)
        except Exception as e:
            logger.error(f"❌ ERREUR WEBHOOK : {str(e)}")
            return HttpResponse("Error", status=500)
            
    return HttpResponse("OK", status=200)

# ==============================================================================
# 3. GESTION DES RETRAITS
# ==============================================================================

@login_required
def demander_retrait(request):
    """Enregistre une demande de retrait le samedi soir."""
    profil = request.user.profil
    maintenant = timezone.now()
    
    if not (maintenant.weekday() == 5 and maintenant.hour >= 18):
        messages.warning(request, "Guichet fermé. Revenez samedi dès 18h.")
        return redirect('dashboard')

    if request.method == 'POST':
        try:
            montant = Decimal(request.POST.get('montant', '0').replace(',', '.'))
            numero = request.POST.get('telephone', '').strip()

            if montant < 1000:
                messages.error(request, "Minimum de retrait : 1000 FCFA.")
            elif montant > profil.solde:
                messages.error(request, "Solde insuffisant.")
            elif len(numero) < 8:
                messages.error(request, "Numéro invalide.")
            else:
                with transaction.atomic():
                    profil.solde -= montant
                    profil.save()
                    Retrait.objects.create(
                        profil=profil, 
                        montant=montant, 
                        numero_paiement=numero, 
                        statut='EN_ATTENTE'
                    )
                messages.success(request, f"🚀 Demande de {montant} XAF enregistrée.")
                return redirect('dashboard')
        except (InvalidOperation, ValueError):
            messages.error(request, "Montant invalide.")

    return render(request, 'ponzi/retrait.html', {'profil': profil})