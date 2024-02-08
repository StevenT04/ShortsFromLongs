from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django import forms
from .forms import ChunkingForm, ProcessingForm  # Assume you have created these forms



# Create your views here.
def show_home(request):
    form = ChunkingForm()  # Instantiate your form
    return render(request, 'home.html', {'form': form})  # Pass it in the context here

def show_about(request):
    return render(request, 'about.html')

def show_videos(request):
    return render(request, 'videos.html')

def process_form(request):
    if request.method == 'POST':
        form = ChunkingForm(request.POST)
        if form.is_valid():
            # Logic to handle chunking
            # After processing, you can pass necessary data to the videos page via session or redirect URL
            return HttpResponseRedirect('/video-list/')
        else:
            # Redirect back to home with form errors
            return render(request, 'home.html', {'form': form})

    # If not POST, redirect to home page
    return redirect('page_home')


def show_processing(request):
    return HttpResponse("No Processing page yet")


