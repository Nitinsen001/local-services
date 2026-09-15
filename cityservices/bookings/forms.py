from django import forms
from django.utils import timezone
from datetime import datetime

from .models import Booking


class BookingForm(forms.ModelForm):
    full_name = forms.CharField(max_length=150)
    email = forms.EmailField()
    phone = forms.CharField(max_length=30)
    address = forms.CharField(widget=forms.Textarea, max_length=500)
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    time = forms.TimeField(input_formats=['%H:%M'])

    class Meta:
        model = Booking
        fields = ['date', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 4}),
        }

    def clean_date(self):
        value = self.cleaned_data['date']
        if value < timezone.localdate():
            raise forms.ValidationError('Please choose a future date and time.')
        return value

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('full_name') and cleaned.get('phone') and cleaned.get('address'):
            details = (
                f"Customer: {cleaned['full_name']} | Phone: {cleaned['phone']} | "
                f"Email: {cleaned['email']} | Address: {cleaned['address']}"
            )
            cleaned['notes'] = f"{details} | {cleaned.get('notes', '')}".strip(' |')
        if cleaned.get('date') and cleaned.get('time'):
            booking_date = timezone.make_aware(datetime.combine(cleaned['date'], cleaned['time']))
            if booking_date <= timezone.now():
                self.add_error('date', 'Please choose a future date and time.')
            cleaned['date'] = booking_date
        return cleaned