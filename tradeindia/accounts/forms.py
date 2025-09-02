from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, UserProfile

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=15, required=False)
    state = forms.CharField(max_length=100, required=False)
    district = forms.CharField(max_length=100, required=False)
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'phone_number', 'state', 'district', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.phone_number = self.cleaned_data.get('phone_number')
        user.state = self.cleaned_data.get('state')
        user.district = self.cleaned_data.get('district')
        if commit:
            user.save()
        return user

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'website', 'date_of_birth', 'preferred_categories']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }