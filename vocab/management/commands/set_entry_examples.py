from pprint import pprint

from django.core.management import BaseCommand, CommandError
from django.db import DatabaseError

from vocab.bbc import NewsReview
from vocab.models import Entry


class Command(BaseCommand):
    help = 'Set examples based on entries.'

    def handle(self, *args, **options):
        entries = Entry.objects.all()
        episodes_with_entries = set()
        for entry in entries:
            episodes_with_entries.add(entry.episode)

        for e in episodes_with_entries:
            entries = e.entry_set.all()
            episode_content = e.raw_content.split('\n')
            for entry in entries:
                idx = None
                try:
                    idx = episode_content.index(f'{entry.term}\r')
                except ValueError:
                    idx = episode_content.index(entry.term)
                finally:
                    entry.examples = f'{episode_content[idx+2]}{episode_content[idx+3]}'
                    entry.save()

        self.stdout.write(self.style.SUCCESS(f'All examples set.'))
