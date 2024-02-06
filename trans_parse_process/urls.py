from django.urls import path
from . import views

urlpatterns = [
    path('', views.show_home, name='page_home'),
    path('about/', views.show_about, name='page_about'),
    path('chunks/', views.show_chunks, name='page_chunks'),
    path('process-form/', views.process_form, name='page_process_form'),
    path('processing/', views.show_processing, name='page_processing')
]