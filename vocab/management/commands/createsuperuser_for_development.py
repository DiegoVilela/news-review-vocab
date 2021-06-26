from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    """Create a superuser for development environment"""

    def handle(self, *args, **options):
        User = get_user_model()
        if User.objects.exists():
            return

        admin = User.objects.create_superuser(username='admin', password='123')

        self.stdout.write(f'Super user "{admin.username}" was created.')
