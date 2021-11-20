from django.shortcuts import render, redirect, get_object_or_404
from .forms import VideoForm, SearchForm
from django.contrib import messages
from .models import Video
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models.functions import Lower

# Create your views here.
def home(request):
    app_name = 'Hydraulic Compressor Videos'
    return render(request, 'video_collection/home.html', {'app_name' : app_name})

def add(request):

    if request.method == 'POST':
        new_video_form = VideoForm(request.POST)
        if new_video_form.is_valid():
            try:
                new_video_form.save()
                # messages.info(request, 'New video saved!')
                # todo show success message or redirect to list of videos
                return redirect('video_list')
            except ValidationError:
                messages.warning(request, 'Invalid YouTube URL')
            except IntegrityError:
                messages.warning(request, 'Error: video was previously added to your database')    

        messages.warning(request, 'Please check the info entered.')
        return render(request, 'video_collection/add.html', {'new_video_form': new_video_form})

    new_video_form = VideoForm()
    return render(request, 'video_collection/add.html', {'new_video_form': new_video_form})

def video_list(request):

    search_form = SearchForm(request.GET) # build form from data user has sent to app

    if search_form.is_valid():
        search_term = search_form.cleaned_data['search_term'] # example: 'lego' 'fruit
        videos = Video.objects.filter(name__icontains=search_term).order_by(Lower('name')) # will match all videos where name (case insensitive) matches search term

    else: # form is not filled in or this is the first time the user sees the page
        search_form = SearchForm()
        videos = Video.objects.all().order_by(Lower('name'))
    
    return render(request, 'video_collection/video_list.html', {'videos': videos, 'search_form': search_form})

def video_detail(request, video_pk):
    video = get_object_or_404(Video, pk=video_pk)
    return render(request, 'video_collection/video_detail.html', {'video': video})