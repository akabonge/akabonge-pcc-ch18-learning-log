from django.shortcuts import render, redirect
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum

from .models import Topic, Entry
from .forms import TopicForm, EntryForm


def index(request):
    """Home page for Learning Log."""
    return render(request, 'learning_logs/index.html')


@login_required
def topics(request):
    """Show all topics owned by the current user."""
    topics = Topic.objects.filter(owner=request.user).order_by('date_added')
    return render(request, 'learning_logs/topics.html', {'topics': topics})


@login_required
def topic(request, topic_id):
    """Show a single topic and its entries; protect cross-user access."""
    topic = Topic.objects.get(id=topic_id)
    if topic.owner != request.user:
        raise Http404

    entries = topic.entry_set.order_by('-date_added')
    return render(request, 'learning_logs/topic.html', {'topic': topic, 'entries': entries})


@login_required
def new_topic(request):
    """Add a new topic."""
    if request.method != 'POST':
        form = TopicForm()
    else:
        form = TopicForm(data=request.POST)
        if form.is_valid():
            new_topic = form.save(commit=False)
            new_topic.owner = request.user
            new_topic.save()
            return redirect('learning_logs:topics')

    return render(request, 'learning_logs/new_topic.html', {'form': form})


@login_required
def new_entry(request, topic_id):
    """Add a new entry for a particular topic."""
    topic = Topic.objects.get(id=topic_id)
    if topic.owner != request.user:
        raise Http404

    if request.method != 'POST':
        form = EntryForm()
    else:
        form = EntryForm(data=request.POST)
        if form.is_valid():
            new_entry = form.save(commit=False)
            new_entry.topic = topic
            new_entry.save()
            return redirect('learning_logs:topic', topic_id=topic_id)

    return render(request, 'learning_logs/new_entry.html', {'topic': topic, 'form': form})


@login_required
def edit_entry(request, entry_id):
    """Edit an existing entry."""
    entry = Entry.objects.get(id=entry_id)
    topic = entry.topic
    if topic.owner != request.user:
        raise Http404

    if request.method != 'POST':
        form = EntryForm(instance=entry)
    else:
        form = EntryForm(instance=entry, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('learning_logs:topic', topic_id=topic.id)

    return render(request, 'learning_logs/edit_entry.html', {
        'entry': entry,
        'topic': topic,
        'form': form,
    })


@login_required
def metrics(request):
    """Show learning metrics (hours logged) for the current user."""
    totals_by_topic = (
        Entry.objects
        .filter(topic__owner=request.user)
        .values('topic__text')
        .annotate(total_hours=Sum('hours_spent'))
        .order_by('-total_hours')
    )

    total_hours_all = (
        Entry.objects
        .filter(topic__owner=request.user)
        .aggregate(total=Sum('hours_spent'))['total'] or 0
    )

    return render(request, 'learning_logs/metrics.html', {
        'totals_by_topic': totals_by_topic,
        'total_hours_all': total_hours_all,
    })
