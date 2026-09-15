from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.RadioSelect(attrs={
                'class': 'star-input',
                'id': 'star{{ forloop.counter }}'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Share details of your experience with this service. What did you like? What could be improved?',
                'maxlength': '500',
                'required': True
            })
        }
        labels = {
            'rating': 'How would you rate this service?',
            'comment': 'Your Review'
        }