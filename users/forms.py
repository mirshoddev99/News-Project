from django.contrib.auth.forms import AuthenticationForm

from .models import Profile

from django import forms
from django.contrib.auth.models import User


class UserRegistrationForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 500px;'}))
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 500px;'}))
    email = forms.CharField(widget=forms.EmailInput(attrs={'class': 'form-control', 'style': 'width: 500px;'}))
    password = forms.CharField(label="Password",
                               widget=forms.PasswordInput(attrs={'class': 'form-control', 'style': 'width: 500px;'}))
    password2 = forms.CharField(label="Password2",
                                widget=forms.PasswordInput(attrs={'class': 'form-control', 'style': 'width: 500px;'}))

    class Meta:
        model = User
        fields = ["username", "first_name", "email"]

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords don\'t match.')
        return cd['password2']

    def clean_email(self):
        cd = self.cleaned_data
        if User.objects.filter(email=cd['email']).exists():
            raise forms.ValidationError('Email already in user')
        return cd['email']


class UserEditForm(forms.ModelForm):
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 500px;'}))
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 500px;'}))
    email = forms.CharField(widget=forms.EmailInput(attrs={'class': 'form-control', 'style': 'width: 500px;'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class ProfileEditForm(forms.ModelForm):
    birth_date = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 500px;'}))

    class Meta:
        model = Profile
        fields = ['birth_date', 'photo']


class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 500px;'})
    )
    password = forms.CharField(label="Password",
                               widget=forms.PasswordInput(attrs={'class': 'form-control', 'style': 'width: 500px;'}))
