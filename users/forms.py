from django import forms
from django.contrib.auth.models import User
from .models import Profil
from django.core.exceptions import ValidationError

class InscriptionForm(forms.ModelForm):
    # 1. Définition des champs avec tes widgets et design
    nom = forms.CharField(
        label="Nom", 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre nom'})
    )
    prenom = forms.CharField(
        label="Prénom", 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre prénom'})
    )
    email = forms.EmailField(
        label="Adresse Email", 
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Ex: exemple@mail.com'})
    )
    telephone = forms.CharField(
        label="Téléphone", 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 6XXXXXXXX'})
    )
    password = forms.CharField(
        label="Mot de passe",
        min_length=6,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '6 caractères minimum'})
    )
    confirm_password = forms.CharField(
        label="Confirmer le mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Répétez le mot de passe'})
    )

    class Meta:
        model = User
        # IMPORTANT : Tous les champs doivent être listés ici pour éviter les erreurs d'affichage
        fields = ['username', 'email', 'nom', 'prenom', 'telephone', 'password', 'confirm_password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Nom d'utilisateur"}),
        }

    # 2. Méthodes de validation (Clean)
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Cette adresse email est déjà utilisée par un autre compte.")
        return email

    def clean_telephone(self):
        tel = self.cleaned_data.get('telephone')
        if Profil.objects.filter(telephone=tel).exists():
            raise ValidationError("Ce numéro de téléphone est déjà utilisé.")
        return tel

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm = cleaned_data.get("confirm_password")
        if password and confirm and password != confirm:
            self.add_error('confirm_password', "Les deux mots de passe ne sont pas identiques.")
        return cleaned_data

    # 3. Logique de sauvegarde
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.last_name = self.cleaned_data['nom']
        user.first_name = self.cleaned_data['prenom']
        user.set_password(self.cleaned_data['password'])
        
        if commit:
            user.save()
            # On récupère le profil (créé automatiquement par ton signal post_save)
            # et on met à jour le téléphone
            try:
                profil = user.profil
            except Profil.DoesNotExist:
                profil = Profil.objects.create(user=user)
            
            profil.telephone = self.cleaned_data['telephone']
            profil.save()
        return user