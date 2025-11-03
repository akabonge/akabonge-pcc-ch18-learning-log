from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404
from .models import Topic

def index(request):
    return render(request, 'learning_logs/index.html')

def topics(request):
    topics = Topic.objects.order_by('date_added')
    return render(request, 'learning_logs/topics.html', {'topics': topics})

def topic(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id)
    entries = topic.entry_set.order_by('-date_added')
    return render(request, 'learning_logs/topic.html', {'topic': topic, 'entries': entries})


