from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django import forms
from .forms import ChunkingForm, ProcessingForm  # Assume you have created these forms



# Create your views here.
def show_home(request):
    form = ChunkingForm()  # Instantiate your form
    return render(request, 'home.html', {'form': form})  # Pass it in the context here

def show_about(request):
    return render(request, 'about.html')

def show_chunks(request):
    if request.method == 'POST':
        form = ChunkingForm(request.POST)
        if form.is_valid():
            # Logic to handle chunking
            pass  # Replace with actual logic
    else:
        form = ChunkingForm()
    return render(request, 'chunks.html', {'form': form})

def show_processing(request):
    return HttpResponse("No Processing page yet")
# def show_processing(request):
#     if request.method == 'POST':
#         form = ProcessingForm(request.POST)
#         if form.is_valid():
#             # Logic to handle processing
#             pass  # Replace with actual logic
#     else:
#         form = ProcessingForm()
#     return render(request, 'processing.html', {'form': form})

