from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import date

class Video(models.Model):
    url = models.URLField(max_length=1024, unique=True)  # Source URL
    video_file = models.FileField(upload_to='videos/')  # Path to the downloaded video
    title = models.CharField(max_length=255)  # Video title
    # processed = models.BooleanField(default=False)  # Processing status #TODO: Is this really needed?
    slug = models.SlugField(unique=True, blank=True)  # NEW: Slug field for pretty URLs

    def get_absolute_url(self):  # NEW: Method to get absolute URL
        return reverse('video_detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):  # NEW: Custom save method
        if not self.slug:
            self.slug = slugify(self.title)
            # Ensure uniqueness of the slug
            original_slug = self.slug
            counter = 1
            while Video.objects.filter(slug=self.slug).exclude(id=self.id).exists():
                self.slug = f'{original_slug}-{counter}'
                counter += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Transcript(models.Model):
    video = models.OneToOneField(Video, on_delete=models.CASCADE)  # Link to the Video
    full_transcript = models.TextField()  # Full transcript text
    # structured_transcript = models.TextField()  # Structured format for processing #TODO: Is this really needed?
    # Consider adding a slug or other fields here if needed for direct access or SEO purposes

    def __str__(self):
        return f"Transcript for {self.video.title}"

class ShortClip(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE)  # Link to the original Video
    start_time = models.DurationField()  # Clip start time
    end_time = models.DurationField()  # Clip end time
    clip_file = models.FileField(upload_to='clips/')  # Path to the processed clip
    title = models.CharField(max_length=255)  # Short title or description of the clip
    slug = models.SlugField(unique=True, blank=True)  # NEW: Slug field

    def get_absolute_url(self):  # NEW: Method to get absolute URL
        return reverse('clip_detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):  # NEW: Custom save method for slug
        if not self.slug:
            self.slug = slugify(self.title)
            # Ensure uniqueness of the slug
            original_slug = self.slug
            counter = 1
            while ShortClip.objects.filter(slug=self.slug).exclude(id=self.id).exists():
                self.slug = f'{original_slug}-{counter}'
                counter += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Clip: {self.title} from {self.video.title}"
