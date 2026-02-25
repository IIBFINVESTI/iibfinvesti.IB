import os
import sys
import django

# 1. Ajoute le chemin de ton projet au système
# Sur PythonAnywhere, ce sera /home/iibfaraba/iibfinvesti.IB
# On utilise un chemin relatif pour que ça marche aussi sur ton PC
base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(base_dir)

# 2. Configure les réglages Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# 3. Importe ta fonction de distribution
# (Assure-tu que ton script est dans un fichier nommé utils.py dans le dossier ponzi)
try:
    from ponzi.utils import distribuer_gains_quotidiens
    
    print("Début de la distribution des gains...")
    resultat = distribuer_gains_quotidiens()
    print(f"TERMINÉ : {resultat}")

except Exception as e:
    print(f"ERREUR lors de la distribution : {e}")