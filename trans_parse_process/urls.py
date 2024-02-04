from django.urls import path
from . import views

urlpatterns = [
    path('', views.show_home, name='page_home'),
    path('about/', views.show_about, name='page_about'),
    path('chunks/', views.show_chunks, name='page_chunks'),
    path('processing/', views.show_processing, name='page_processing')

]