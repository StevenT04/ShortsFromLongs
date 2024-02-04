from django import forms
import re

class ChunkingForm(forms.Form):
    youtube_url = forms.URLField(label='YouTube URL')

def clean_youtube_url(self):
    url = self.cleaned_data.get('youtube_url', '')
    youtube_regex = r'^https:\/\/(www\.)?(youtube\.com\/watch\?v=|youtu\.be\/)[A-Za-z0-9_-]{11}$'
    if not re.fullmatch(youtube_regex, url):
        raise forms.ValidationError('Please enter a valid YouTube URL.')
    return url



class ProcessingForm(forms.Form):
    timestamps = forms.CharField(widget=forms.Textarea, label='Formatted Timestamps')
