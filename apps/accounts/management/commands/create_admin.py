from decouple import config
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = "Cria o superusuário a partir das variáveis ADMIN_EMAIL e ADMIN_PASSWORD. Idempotente."

    def handle(self, *args, **options):
        email = config("ADMIN_EMAIL", default="")
        password = config("ADMIN_PASSWORD", default="")

        if not email or not password:
            self.stdout.write("ADMIN_EMAIL ou ADMIN_PASSWORD não definidos — pulando criação do admin.")
            return

        if User.objects.filter(email=email).exists():
            self.stdout.write(f"Admin {email} já existe — nenhuma ação necessária.")
            return

        User.objects.create_superuser(email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f"Superusuário {email} criado com sucesso."))
