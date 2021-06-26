from django.core.management import BaseCommand, CommandError
from django.db import DatabaseError

from vocab.bbc import NewsReview


class Command(BaseCommand):
    help = 'Fetch and save episodes from BBC News Review.'

    def handle(self, *args, **options):
        handler = NewsReview()
        result = handler.pull()
        if result:
            try:
                for episode in result:
                    episode.save()
            except DatabaseError as e:
                raise CommandError(e)

        self.stdout.write(self.style.SUCCESS(f'All updated.'))
