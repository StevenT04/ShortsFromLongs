from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

TOPIC_CHOICES = [
    ('science', 'Science'),
    ('education', 'Education'),
    ('entertainment', 'Entertainment'),
    ('other', 'Other'),
]

class Video(models.Model):
    url = models.URLField(max_length=1024, unique=True)  # Source URL
    video_file = models.FileField(upload_to='videos/', unique=True)  # Path to the downloaded video
    topic = models.CharField(
        max_length=255,
        choices=TOPIC_CHOICES,
        default='other'
    )    
    title = models.CharField(max_length=255, unique=True)  # Video title
    thumbnail = models.ImageField(upload_to='thumbnails', default='default_image.png')
    slug = models.SlugField(unique=True, blank=True)  # Slug field for pretty URLs

    def get_absolute_url(self):
        return reverse('video_detail', kwargs={'video_slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            original_slug = self.slug
            counter = 1
            while Video.objects.filter(slug=self.slug).exclude(id=self.id).exists():
                self.slug = f'{original_slug}-{counter}'
                counter += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Chunk(models.Model):
    video = models.ForeignKey(Video, related_name='chunks', on_delete=models.CASCADE)
    text = models.TextField()  # Part of the transcript

    def __str__(self):
        return f"Chunk for {self.video.title}"

class ShortClip(models.Model):
    video = models.ForeignKey(Video, related_name='clips', on_delete=models.CASCADE)
    start_time = models.DurationField()
    end_time = models.DurationField()
    clip_file = models.FileField(upload_to='clips/', null=True)
    description = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)

    def duration(self):
        duration = self.end_time - self.start_time
        # Format the duration as you like. Here's a simple example:
        total_seconds = int(duration.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours}h {minutes}m {seconds}s"
    
    def get_absolute_url(self):
        return reverse('clip_detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.description)
            original_slug = self.slug
            counter = 1
            while ShortClip.objects.filter(slug=self.slug).exclude(id=self.id).exists():
                self.slug = f'{original_slug}-{counter}'
                counter += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Clip: {self.description} from {self.video.title}"
