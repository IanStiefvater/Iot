from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from login.models import usuarios

class Command(BaseCommand):
    help = 'Crea un nuevo usuario'

    def handle(self, *args, **options):
        user = usuarios(nombre='Ian', apellido='Stiefvater', email='ianstiefvater49@gmail.com', contrasena=make_password('653489'))
        user.save()
        self.stdout.write(self.style.SUCCESS('Usuario creado correctamente'))
