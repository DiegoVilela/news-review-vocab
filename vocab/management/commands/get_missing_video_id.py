from django.core.management import BaseCommand, CommandError
from vocab.models import Episode
from vocab.youtube import service


class Command(BaseCommand):
    help = 'Get missing video ids from Youtube.'

    def handle(self, *args, **options):
        episode = Episode.objects.filter(video__isnull=True).first()
        if video_id := service.get_video_id(episode.headline, episode.date):
            episode.video = video_id
            episode.save(update_fields=['video'])
        else:
            raise CommandError(f'Video not found: Episode {episode}')

        self.stdout.write(self.style.SUCCESS(f'Episode {episode} video was updated.'))
