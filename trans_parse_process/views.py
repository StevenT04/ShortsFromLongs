from django.shortcuts import render, redirect
from pytube import YouTube
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from .models import Video
from django.contrib import messages
import requests
from django import forms
import os
from .forms import ChunkingForm, ProcessingForm  # Assume you have created these forms
from django.db.utils import IntegrityError



# Create your views here.
def show_home(request):
    form = ChunkingForm()  # Instantiate your form
    return render(request, 'home.html', {'form': form})  # Pass it in the context here

def show_about(request):
    return render(request, 'about.html')

def show_video_list(request):
    videos = Video.objects.all()
    return render(request, 'video_list.html', {'videos': videos})

def process_form(request):
    if request.method == 'POST':
        form = ChunkingForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['youtube_url']
            title = form.cleaned_data['youtube_title']

            # Check if the video already exists in the database
            if Video.objects.filter(url=url).exists():
                messages.error(request, 'This video has already been downloaded.')
                return render(request, 'home.html', {'form': form})
            
            yt = YouTube(url)
            stream = yt.streams.filter(file_extension='mp4').first()
            if stream:
                # Generate the filename
                filename = title + '.mp4'
                save_path = os.path.join(settings.MEDIA_ROOT, 'videos')
                file_path = os.path.join(save_path, filename)
                
                # Check if the file already exists
                if os.path.exists(file_path):
                    messages.error(request, 'This video has already been downloaded.')
                    return render(request, 'home.html', {'form': form})
                
                # Download video
                stream.download(output_path=save_path, filename=filename)

                # Download thumbnail
                thumbnail_url = yt.thumbnail_url
                response = requests.get(thumbnail_url)
                if response.status_code == 200:
                    thumbnail_filename = title + '.jpg'
                    thumbnail_path = os.path.join(settings.MEDIA_ROOT, 'thumbnails', thumbnail_filename)
                    with open(thumbnail_path, 'wb') as file:
                        file.write(response.content)
                    thumbnail_file = os.path.join('thumbnails', thumbnail_filename)
                else:
                    # Use default thumbnail if download fails
                    thumbnail_file = 'default_image.png'
                    messages.warning(request, 'Failed to download thumbnail, using default.')

                # Create a new Video instance and save it to the database
                video = Video(
                    url=url,
                    video_file=os.path.join('videos', filename),
                    title=title,
                    thumbnail=thumbnail_file
                )
                try:
                    video.save()
                except IntegrityError:
                    messages.error(request, 'This video cannot be saved due to a conflict with existing data.')
                    # Optional: remove the files if they were downloaded but not saved in the database
                    os.remove(file_path)
                    if thumbnail_file != 'default_image.png':
                        os.remove(thumbnail_path)
                    return render(request, 'home.html', {'form': form})

                # Redirect to the video list page
                messages.success(request, 'Video downloaded successfully.')
                return HttpResponseRedirect('/video-list/')
            else:
                messages.error(request, 'No mp4 streams found for this video.')
                return render(request, 'home.html', {'form': form})
        else:
            # If form is not valid
            return render(request, 'home.html', {'form': form})
    else:
        # If not POST, redirect to home page
        return redirect('page_home')



def show_processing(request):
    return HttpResponse("No Processing page yet")


