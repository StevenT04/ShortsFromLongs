from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect


# Create your views here.
def show_home(request):
    return render(request, 'home.html')

def show_about(request):
    return render(request, 'about.html')

def show_chunks(request):
    return HttpResponse("No chunks page yet")

def show_processing(request):
    return HttpResponse("No Processing page yet")

