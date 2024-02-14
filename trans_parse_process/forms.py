from django import forms
import re
from .models import TOPIC_CHOICES

class ChunkingForm(forms.Form):
    youtube_url = forms.URLField(label='YouTube URL')
    youtube_title = forms.CharField(max_length=255, label='Video Title')
    youtube_topic = forms.ChoiceField(
        choices=TOPIC_CHOICES,
        label='Video Topic'
    )
    def clean_youtube_url(self):
        url = self.cleaned_data.get('youtube_url', '')
        youtube_regex = r'^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube(-nocookie)?\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$'
        
        if not re.fullmatch(youtube_regex, url):
            raise forms.ValidationError('Please enter a valid YouTube URL.')
        return url




class ProcessingForm(forms.Form):
    chatgpt_output = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Paste ChatGPT output here'}),
                                     label='ChatGPT Output')

    def clean_chatgpt_output(self):
        data = self.cleaned_data['chatgpt_output']
        # Update the regular expression pattern to match timestamps with or without seconds
        # The pattern now includes an optional group for seconds (:SS) in both start and end times.
        pattern = re.compile(r'\[(\d{2}:\d{2}(?::\d{2})?) - (\d{2}:\d{2}(?::\d{2})?)\] (.+)', re.MULTILINE)

        # Split the input into lines and validate each line
        lines = data.splitlines()
        for line in lines:
            if not re.fullmatch(pattern, line):
                raise forms.ValidationError('Invalid format detected. Please ensure all lines follow the correct format: "[HH:MM:SS - HH:MM:SS] Description." or "[HH:MM - HH:MM] Description."')

        # Return the cleaned data
        return data