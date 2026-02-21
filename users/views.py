from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.models import User
import urllib.parse
from decimal import Decimal
from datetime import datetime

# Importation de tes formulaires et modèles
from .forms import InscriptionForm
from .models import Grille, HistoriqueGain, Investissement

# --- 1. VUES D'ACCÈS (Inscription / Connexion) ---

def inscription_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    ref_code = request.GET.get('ref') 
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save()
                    parrain_username = request.POST.get('parrain_nom')
                    if parrain_username:
                        try:
                            parrain_obj = User.objects.get(username=parrain_username)
                            profil = user.profil
                            profil.parrain = parrain_obj
                            profil.save()
                        except User.DoesNotExist:
                            pass 
                    login(request, user)
                    messages.success(request, f"Compte IIBF activé ! Bienvenue {user.username}.")
                    return redirect('dashboard')
            except Exception as e:
                messages.error(request, f"Erreur technique : {e}")
    else:
        form = InscriptionForm()
    return render(request, 'users/inscription.html', {'form': form, 'ref_code': ref_code})

def connexion_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Connexion réussie. Bon retour {user.username} !")
            return redirect('dashboard')
        else:
            messages.error(request, "Identifiants invalides.")
    else:
        form = AuthenticationForm()
    return render(request, 'users/connexion.html', {'form': form})

# --- 2. TABLEAU DE BORD & MARCHÉ ---

@login_required
def dashboard_view(request):
    profil = request.user.profil
    grilles = Grille.objects.all()
    derniers_gains = HistoriqueGain.objects.filter(profil=profil).order_by('-date_distribution')[:5]
    
    gain_du_jour = Decimal('0.00')
    if profil.pack_montant > 0:
        gain_du_jour = (profil.pack_montant * Decimal(str(profil.pourcentage_journalier))) / Decimal('100')

    maintenant = datetime.now()
    if maintenant.hour >= 20:
        if profil.derniere_maj_gain != maintenant.date() and profil.pack_montant > 0:
            profil.solde += gain_du_jour
            profil.derniere_maj_gain = maintenant.date()
            profil.save()
            HistoriqueGain.objects.create(profil=profil, montant=gain_du_jour)
            messages.success(request, f"Gain de {gain_du_jour} FCFA crédité.")

    return render(request, 'ponzi/dashboard.html', {
        'profil': profil,
        'grilles': grilles,
        'derniers_gains': derniers_gains,
        'gain_du_jour': gain_du_jour,
    })

@login_required
def catalogue_packs_view(request):
    """ Cette vue manquante qui causait l'erreur AttributeError """
    grilles = Grille.objects.all()
    return render(request, 'ponzi/marches.html', {'grilles': grilles, 'profil': request.user.profil})

# --- 3. ACTIONS D'INVESTISSEMENT ---

@login_required
def investir_maintenant(request, grille_id):
    grille = get_object_or_404(Grille, id=grille_id)
    votre_numero = "237687391981" 
    texte = (f"Bonjour IIBF, je souhaite investir dans le pack {grille.nom} "
             f"({grille.montant} FCFA).\nMon ID : {request.user.username}")
    url_whatsapp = f"https://wa.me/{votre_numero}?text={urllib.parse.quote(texte)}"
    return redirect(url_whatsapp)

@login_required
def valider_investissement(request, grille_id):
    if request.method == 'POST':
        grille = get_object_or_404(Grille, id=grille_id)
        profil = request.user.profil
        if profil.solde >= grille.montant:
            try:
                with transaction.atomic():
                    profil.solde -= grille.montant
                    profil.pack_nom = grille.nom
                    profil.pack_montant = grille.montant
                    profil.pourcentage_journalier = grille.pourcentage_gain
                    profil.save()
                    Investissement.objects.create(profil=profil, pack=grille, actif=True)
                messages.success(request, f"Pack {grille.nom} activé !")
            except Exception as e:
                messages.error(request, f"Erreur : {e}")
        else:
            messages.error(request, "Solde insuffisant.")
    return redirect('dashboard')

# --- 4. DÉCONNEXION ---

def deconnexion_view(request):
    if request.method == 'POST':
        logout(request)
        messages.info(request, "Session fermée.")
        return redirect('connexion')
    return redirect('dashboard')