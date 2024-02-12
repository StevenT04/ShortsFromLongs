from django.urls import path
from . import views

urlpatterns = [
    path('', views.show_home, name='page_home'),
    path('about/', views.show_about, name='page_about'),
    path('process-form/', views.process_form, name='page_process_form'),
    path('processing/', views.show_processing, name='page_processing'),
    path('video-list/', views.show_video_list, name='page_video_list'),
    path('video-detail/<int:video_id>/', views.video_detail, name='video_detail'),
    path('process-clips/<int:video_id>/', views.process_clips_form, name='process_clips_form'),
    path('chunk-video/<int:video_id>/', views.chunk_video, name='chunk_video'),
    path('<int:video_id>/delete/', views.delete_video, name='delete_video'),
    path('confirm-delete/<int:video_id>/', views.confirm_delete_video, name='confirm_delete_video')
]