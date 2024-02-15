from django.urls import path
from . import views

urlpatterns = [
    path('', views.show_home, name='page_home'),
    path('about/', views.show_about, name='page_about'),
    path('process-form/', views.process_form, name='page_process_form'),
    path('video-list/', views.show_video_list, name='page_video_list'),
    path('video-detail/<int:video_id>/', views.video_detail, name='video_detail'),
    path('chunk-video/<int:video_id>/', views.chunk_video, name='chunk_video'),
    path('<int:video_id>/delete/', views.delete_video, name='delete_video'),
    path('confirm-delete/<int:video_id>/', views.confirm_delete_video, name='confirm_delete_video'),
    path('processing/<int:video_id>/', views.show_processing, name='page_processing'),
    path('confirm-delete-templates/<int:video_id>/', views.confirm_delete_templates, name='confirm_delete_templates'),
    path('<int:video_id>/delete-templates/', views.delete_templates, name='delete_templates'),
    path('manage-clips/<int:video_id>/', views.manage_clips, name='manage_clips'),
    path('download-clip/<int:clip_id>/', views.download_clip, name='download_clip'),
    path('confirm-delete-clip/<int:clip_id>/', views.confirm_delete_clip, name='confirm_delete_clip'),
    path('<int:clip_id>/delete-clip/', views.delete_clip, name='delete_clip')

]