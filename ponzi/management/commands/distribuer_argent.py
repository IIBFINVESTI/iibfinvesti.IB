from django.core.management.base import BaseCommand
from ponzi.utils import distribuer_gains_quotidiens

class Command(BaseCommand):
    help = 'Distribue les gains quotidiens aux investisseurs actifs'

    def handle(self, *args, **kwargs):
        self.stdout.write("Début de la distribution...")
        resultat = distribuer_gains_quotidiens()
        self.stdout.write(self.style.SUCCESS(resultat))