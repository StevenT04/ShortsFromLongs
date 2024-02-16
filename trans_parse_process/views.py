from django.urls import reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404, reverse
from pytube import YouTube
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.utils.translation import gettext as _
from .models import Video, Chunk, ShortClip, TOPIC_CHOICES
import re
from datetime import timedelta
import ffmpeg
from django.contrib import messages
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
import time
import requests
from django import forms
import os
from .forms import ChunkingForm, ProcessingForm 
from django.db.utils import IntegrityError
from django.db.models import Q
import ffmpeg
import cv2



# Create your views here.
def show_home(request):
    form = ChunkingForm()  # Instantiate your form
    return render(request, 'home.html', {'form': form})  # Pass it in the context here

def show_about(request):
    return render(request, 'about.html')


def show_video_list(request):
    topic_videos = []
    for topic_choice in TOPIC_CHOICES:
        topic_code, topic_name = topic_choice
        videos_in_topic = Video.objects.filter(topic=topic_code)
        if videos_in_topic.exists():
            topic_videos.append((topic_name, videos_in_topic))
    
    return render(request, 'video_list.html', {'topic_videos': topic_videos})

def delete_video(request, video_id=None, video_slug=None):
    video = get_object_or_404(Video, pk=video_id)
    
    # Build the path for the video file and thumbnail
    video_file_path = os.path.join(settings.MEDIA_ROOT, str(video.video_file))
    thumbnail_path = os.path.join(settings.MEDIA_ROOT, str(video.thumbnail))

    # Delete the video file if it exists
    if os.path.isfile(video_file_path):
        os.remove(video_file_path)
    # Delete the thumbnail file if it exists and isn't the default image
    if os.path.isfile(thumbnail_path) and 'default_image.png' not in thumbnail_path:
        os.remove(thumbnail_path)

    # Now, delete the video object
    video.delete()
    messages.add_message(request, messages.INFO, _('Video Deleted'))
    
    return HttpResponseRedirect(reverse_lazy('page_video_list'))

def confirm_delete_video(request, video_id=None, video_slug=None):
    video = get_object_or_404(Video, pk=video_id)
    if request.method == 'POST':
        # Proceed with deletion if the form is submitted
        return delete_video(request, video_id=video.id, video_slug=video.slug)
    else:
        # Show confirmation page
        return render(request, 'confirm_delete.html', {'video': video})


def process_form(request):
    if request.method == 'POST':
        form = ChunkingForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['youtube_url']
            title = form.cleaned_data['youtube_title']
            topic = form.cleaned_data['youtube_topic']

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
                    thumbnail=thumbnail_file,
                    topic=topic
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
    
def video_detail(request, video_id):
    video = get_object_or_404(Video, pk=video_id)
    chunks = video.chunks.all()  # Assuming a related_name='chunks' in the Video model
    form = ProcessingForm()
    # Additional context as necessary for processing and clips
    return render(request, 'video_detail.html', {'video': video, 'chunks': chunks})

def chunk_video(request, video_id):
    video = get_object_or_404(Video, pk=video_id)
    # Check if chunks already exist for this video
    if video.chunks.exists():
        video.chunks.all().delete()
        messages.info(request, "Existing Chunks Deleted, Re-Chunked now.")
        

    try:
        video_id = parse_qs(urlparse(video.url).query).get('v', [None])[0]
        if not video_id:
            raise Exception("Invalid YouTube URL.")
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        chunks = get_and_split_transcript(transcript, video.title, 17000)
        
        # Save chunks to database
        for chunk_text in chunks:
            Chunk.objects.create(video=video, text=chunk_text)
        messages.success(request, "Video transcript chunked successfully.")
    except Exception as e:
        messages.error(request, f"Failed to chunk transcript: {e}")
    
    return redirect('video_detail', video_id=video.id)

# ...

def get_and_split_transcript(transcript, video_title, chunk_size):
    prompt_template = (
        "I want you to only answer in English. Your goal is to extract interesting key takeaways of the next chunk of the transcript. "
        "Takeaways MUST be OVER 1 MINUTE IN LENGTH and LESS THAN 3 MINUTES IN LENGTH."
        " They have to be VIRAL, INTERESTING, INFORMATIVE, and EASY to READ and UNDERSTAND.\n"
        "Each key takeaway must be a list item, of the following format:\n\n"
        "- [Timestamp Duration] [Takeaway emoji] [Key takeaway in English]\n\n"
        "The timestamp should be presented in a duration format. The first set of timestamps should be the start time of the Key Takeaway, "
        "and the second set of timestamps, after the hyphen, should be the end time of the Key Takeaway, for example:\n"
        "[xx:xx - xx:xx]\n"
        "[xx:xx:xxx - yy:yy:yy]\n\n"
        "Keep emoji relevant and unique to each Key Takeaway item. Do not use the same emoji for every takeaway. Render the brackets. "
        "WHEN YOU ANSWER, YOU MUST GIVE YOUR RESPONSE IN A CODE BLOCK INSTEAD OF A NORMAL TEXT OUTPUT.\n"
        "MAKE SURE THERE IS NO LINE SEPERATION BETWEEN EACH TAKEAWAY.\n"
        "MAKE SURE THERE IS NO HYPHEN BEFORE THE TIMESTAMPS\n"
        "Do not prepend takeaway with \"Key takeaway\".\n\n"
        f"[VIDEO TITLE]: {video_title}\n\n"
        "[VIDEO TRANSCRIPT CHUNK]:\n\n"
    )
    
    chunks, current_chunk, current_chunk_size = [], "", 0

    for i in range(0, len(transcript), 5):  # Process every 5th entry
        texts = ' '.join(transcript[j]['text'] for j in range(i, min(i+5, len(transcript))))
        timestamp = time.strftime('%H:%M:%S' if transcript[i]['start'] >= 3600 else '%M:%S', time.gmtime(transcript[i]['start']))
        entry = f"[{timestamp}] {texts}\n"
        
        # Initialize the first chunk with prompt + first entry or append entry to current chunk
        if not chunks and not current_chunk:  # Initialize the first chunk with prompt
            current_chunk = prompt_template
        if current_chunk_size + len(entry) > chunk_size:
            chunks.append(current_chunk)
            current_chunk = prompt_template + entry
            current_chunk_size = len(current_chunk)
        else:
            current_chunk += entry
            current_chunk_size += len(entry)

    if current_chunk.strip() not in [prompt_template.strip(), ""]:  # Ensure not to add empty or only prompt chunks
        chunks.append(current_chunk)

    return chunks

def parse_duration(time_str):
    parts = time_str.split(':')
    if len(parts) == 3:
        hours, minutes, seconds = map(int, parts)
    elif len(parts) == 2:
        hours = 0
        minutes, seconds = map(int, parts)
    else:
        raise ValueError("Invalid timestamp format")
    return timedelta(hours=hours, minutes=minutes, seconds=seconds)



def show_processing(request, video_id):
    video = get_object_or_404(Video, pk=video_id)
    chunks = video.chunks.all()

    if not Chunk.objects.filter(video_id=video_id).exists():
        messages.error(request, "Please load chunks for this video.")
        return redirect('video_detail', video_id=video_id)

    if request.method == 'POST':
        form = ProcessingForm(request.POST)
        if form.is_valid():
            chatgpt_output = form.cleaned_data['chatgpt_output']
            pattern = r'\[(\d{2}:\d{2}(?::\d{2})?) - (\d{2}:\d{2}(?::\d{2})?)\] (.+)'
            matches = re.findall(pattern, chatgpt_output, re.MULTILINE)

            for start, end, description in matches:
                start_time = parse_duration(start)
                end_time = parse_duration(end)
                # Check if a ShortClip with these exact attributes already exists
                if not ShortClip.objects.filter(
                    start_time=start_time,
                    end_time=end_time,
                    description=description
                ).exists():
                    # Only create a new ShortClip if it doesn't exist
                    ShortClip.objects.create(
                        video=video,
                        start_time=start_time,
                        end_time=end_time,
                        description=description,
                        clip_file=None  # Assuming handling of clip_file is done elsewhere or not required for creation
                )
                else:
                    # Optional: Add a message or take some action if the clip already exists
                    messages.info(request, "Clip with similar attributes already exists in this set.")

            messages.success(request, "Clips processed successfully.")
            # Stay on the same page but indicate success
            return render(request, 'processing_page.html', {'video': video, 'chunks': chunks, 'form': ProcessingForm()})  # Reset form
        else:
            # If form is not valid, re-render the page with the form to show validation errors
            messages.error(request, "There was an error processing your form.")
    else:
        form = ProcessingForm()

    # Display the form for GET requests or re-render for invalid POST submissions
    return render(request, 'processing_page.html', {'video': video, 'chunks': chunks, 'form': form})


def confirm_delete_templates(request, video_id):
    video = get_object_or_404(Video, pk=video_id)
    if request.method == 'POST':
        # Call the correct deletion function and pass only video_id
        return delete_templates(request, video_id=video.id)
    else:
        # Show confirmation page
        return render(request, 'confirm_delete_clip_templates.html', {'video': video})

def delete_templates(request, video_id):
    video = get_object_or_404(Video, pk=video_id)
    
    # Assuming 'clips' is the related name for clip templates associated with the video
    video.clips.all().delete()
    messages.add_message(request, messages.INFO, _('Template Clips Deleted'))
    
    # Use 'reverse' for dynamic URL resolution
    return HttpResponseRedirect(reverse_lazy('page_processing', kwargs={'video_id': video.id}))

def manage_clips(request, video_id):
    video = get_object_or_404(Video, pk=video_id)
    clips = video.clips.all()
    return render(request, 'manage_clips.html', {'video': video, 'clips': clips})


def detect_face_and_clip_with_aspect_ratio(input_file, output_file, start_time, duration):
    # Initialize the face detector.
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    # Open the input video file for face detection.
    cap = cv2.VideoCapture(input_file)

    # Fetch video dimensions
    video_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    video_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Set the video's start time for face detection.
    cap.set(cv2.CAP_PROP_POS_MSEC, start_time*1000)

    face_detected = False
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)

        if len(faces) > 0:
            x, y, w, h = faces[0]
            face_detected = True
            break

    cap.release()

    if face_detected:
        aspect_ratio = 9 / 16

        # Start by maximizing height based on the face detection
        max_crop_height = min(video_height, h * 4)  # Adjust multiplier as needed to include more vertical space
        max_crop_width = max_crop_height * aspect_ratio

        # Adjust crop position to ensure the face is centered
        crop_x = max(0, min(x + w/2 - max_crop_width/2, video_width - max_crop_width))
        crop_y = max(0, min(y + h/2 - max_crop_height/2, video_height - max_crop_height))

        # Recalculate dimensions if the adjusted crop exceeds video bounds
        if crop_x + max_crop_width > video_width:
            max_crop_width = video_width - crop_x
            max_crop_height = max_crop_width / aspect_ratio
        if crop_y + max_crop_height > video_height:
            max_crop_height = video_height - crop_y
            max_crop_width = max_crop_height * aspect_ratio

        # Source video and audio streams
        vid_stream = ffmpeg.input(input_file, ss=start_time, t=duration)
        audio_stream = vid_stream.audio

        # Crop video and apply filters for enhancement and vignette effect
        filtered_vid_stream = vid_stream.filter('crop', w=max_crop_width, h=max_crop_height, x=crop_x, y=crop_y)
        # Output - combine enhanced video with original audio
        ffmpeg.output(filtered_vid_stream, audio_stream, output_file, acodec='copy', vcodec='libx264', preset='veryslow', crf=5).run()
    else:
        # If no face was detected, clip the video segment without cropping.
        ffmpeg.input(input_file, ss=start_time, t=duration) \
              .output(output_file, acodec='copy', vcodec='libx264').run()
              
              
def download_clip(request, clip_id):
    clip = get_object_or_404(ShortClip, pk=clip_id)
    
    if clip.clip_file:
        # Clip already exists, redirect or serve the existing file
        # Redirect back to manage clips page
        messages.error(request, "Clip already downloaded.")
        return redirect('manage_clips', video_id=clip.video_id)
    
    input_file = os.path.join(settings.MEDIA_ROOT, str(clip.video.video_file))
    output_file = os.path.join(settings.MEDIA_ROOT, "clips", f"clip_{clip.pk}.mp4")
    
    # Convert DurationField to total seconds
    start_time = clip.start_time.total_seconds()
    duration = (clip.end_time - clip.start_time).total_seconds()
    
    # Call the adapted function
    detect_face_and_clip_with_aspect_ratio(input_file, output_file, start_time, duration)
    
    # After processing, update the clip_file field
    clip.clip_file = os.path.join("clips", f"clip_{clip.pk}.mp4")
    clip.save()
    
    # Redirect back to manage clips page or directly serve the file
    return redirect('manage_clips', video_id=clip.video_id)
    # If you want to directly serve the file, uncomment the following lines:
    # with open(output_file, 'rb') as fh:
    #     response = HttpResponse(fh.read(), content_type="video/mp4")
    #     response['Content-Disposition'] = f'attachment; filename=clip_{clip.pk}.mp4'
    #     return response
    
    
def confirm_delete_clip(request, clip_id=None):
    clip = get_object_or_404(ShortClip, pk=clip_id)
    if request.method == 'POST':
        # Proceed with deletion if the form is submitted
        return delete_clip(request, clip_id=clip.id)
    else:
        # Show confirmation page
        return render(request, 'confirm_delete_clip.html', {'clip': clip})
    
def delete_clip(request, clip_id=None):
    clip = get_object_or_404(ShortClip, pk=clip_id)
    video_id = clip.video.id  # Capture the video_id before deleting the clip
    
    clip_file_path = os.path.join(settings.MEDIA_ROOT, str(clip.clip_file))
    
    # Check if the clip file exists and delete it
    if clip.clip_file and os.path.isfile(clip_file_path):
        os.remove(clip_file_path)
    
    # Delete the clip object
    clip.delete()
    messages.add_message(request, messages.INFO, 'Clip Deleted')
    
    # Correctly use the reverse function to generate the URL for redirection
    manage_clips_url = reverse('manage_clips', kwargs={'video_id': video_id})
    return HttpResponseRedirect(manage_clips_url)


def delete_clip_download(request, clip_id=None):
    clip = get_object_or_404(ShortClip, pk=clip_id)
    video_id = clip.video.id  # Capture the video_id before deleting the clip
    
    clip_file_path = os.path.join(settings.MEDIA_ROOT, str(clip.clip_file))

    # Check if the clip file exists and delete it
    if clip.clip_file:
        clip.clip_file.delete()
        
    if os.path.isfile(clip_file_path):
        os.remove(clip_file_path)
        
    messages.add_message(request, messages.INFO, 'Clip Download Deleted')

    # Correctly use the reverse function to generate the URL for redirection
    manage_clips_url = reverse('manage_clips', kwargs={'video_id': video_id})
    return HttpResponseRedirect(manage_clips_url)
