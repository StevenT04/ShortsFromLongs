from django import forms
import re

class ChunkingForm(forms.Form):
    youtube_url = forms.URLField(label='YouTube URL')
    youtube_title = forms.CharField(max_length=255, label='Video Title')

    def clean_youtube_url(self):
        url = self.cleaned_data.get('youtube_url', '')
        youtube_regex = r'^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube(-nocookie)?\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$'
        
        if not re.fullmatch(youtube_regex, url):
            raise forms.ValidationError('Please enter a valid YouTube URL.')
        return url




class ProcessingForm(forms.Form):
    timestamps = forms.CharField(widget=forms.Textarea, label='Formatted Timestamps')
