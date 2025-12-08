from django import forms
from .models import Topic, Entry

class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ['text']
        labels = {'text': ''}

class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = ['text', 'study_date', 'hours_spent']
        labels = {
            'text': '',
            'study_date': 'Study date',
            'hours_spent': 'Hours spent',
        }
        widgets = {
            'text': forms.Textarea(attrs={'cols': 80}),
            'study_date': forms.DateInput(attrs={'type': 'date'}),
        }
