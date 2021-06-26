from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse


class Episode(models.Model):
    """A session published by BBC News Review"""

    id = models.PositiveSmallIntegerField(
        primary_key=True,
        help_text="The session number on the BBC News Review website."
    )
    headline = models.CharField(max_length=128, unique=True)
    slug = models.SlugField(max_length=128, unique=True)
    date = models.DateField()
    raw_content = models.TextField()
    video = models.CharField(
        max_length=11,
        unique=True,
        null=True,
        help_text="The videoId from Youtube."
    )

    def __str__(self):
        return self.headline

    def get_absolute_url(self):
        return reverse('episode_detail', kwargs={'slug': self.slug})


class Entry(models.Model):
    """The word or phrase presented in an Episode"""

    term = models.CharField(max_length=128, primary_key=True)
    slug = models.SlugField(max_length=128, unique=True)
    meaning = models.CharField(max_length=128)
    examples = models.TextField(max_length=510, blank=True)
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE)

    def __str__(self):
        return self.term

    def get_absolute_url(self):
        return reverse('entry_detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.term)
        return super().save(*args, **kwargs)
