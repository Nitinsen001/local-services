from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile

class RegisterForm(UserCreationForm):
    email = forms.EmailField()
    USER_TYPE_CHOICES = [
        ('user', 'I want to book services'),
        ('provider', 'I want to provide services'),
    ]
    user_type = forms.ChoiceField(
        choices=USER_TYPE_CHOICES,
        widget=forms.RadioSelect,
        label="Account Type"
    )

    # Provider-specific fields
    service_category = forms.ChoiceField(
        choices=Profile.SERVICE_CATEGORIES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Service Category"
    )
    hourly_rate = forms.DecimalField(
        max_digits=8,
        decimal_places=2,
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '50'}),
        label="Hourly Rate (₹)"
    )
    service_area = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Service Area (City/Locality)"
    )
    service_description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        label="Service Description"
    )
    experience = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Years of Experience"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].help_text = (
            'Use at least 8 characters with a mix of letters, numbers and symbols. '
            'Do not use your username or personal information.'
        )
        self.fields['password2'].help_text = 'Enter the same password again.'

    def clean(self):
        cleaned_data = super().clean()
        user_type = cleaned_data.get('user_type')

        # If user is provider, validate provider fields
        if user_type == 'provider':
            if not cleaned_data.get('service_category'):
                raise forms.ValidationError("Service category is required for providers.")
            if not cleaned_data.get('hourly_rate'):
                raise forms.ValidationError("Hourly rate is required for providers.")
            if not cleaned_data.get('service_area'):
                raise forms.ValidationError("Service area is required for providers.")
            if not cleaned_data.get('service_description'):
                raise forms.ValidationError("Service description is required for providers.")
            if not cleaned_data.get('experience'):
                raise forms.ValidationError("Experience is required for providers.")

        return cleaned_data

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class AccountSettingsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }