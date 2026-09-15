from django import forms
from .models import Service, Category
from .models import Availability

class AddServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'price', 'category', 'image', 'location']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'location': forms.TextInput(attrs={'placeholder': 'City, State or specific area'}),
        }


class AvailabilityForm(forms.ModelForm):
    class Meta:
        model = Availability
        fields = ['weekday', 'start_time', 'end_time']
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('start_time') and cleaned.get('end_time') and cleaned['start_time'] >= cleaned['end_time']:
            raise forms.ValidationError('End time must be after start time.')
        return cleaned