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
            # After processing, perhaps redirect to a success page or display the results
            return HttpResponseRedirect('/chunks/')
        else:
            # If the form is not valid, re-render the same page with the form
            # The form will contain the error messages
            return render(request, 'home.html', {'form': form})
    else:
        form = ChunkingForm()
    
    # If it's a GET request, just show the form as usual
    return render(request, 'home.html', {'form': form})


def show_processing(request):
    return HttpResponse("No Processing page yet")


