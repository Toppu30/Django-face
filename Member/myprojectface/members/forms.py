# members/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import *

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'phone_number', 'photo_profile', 'role')

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'phone_number', 'photo_profile', 'role')

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'phone_number', 'photo_profile', 'role')
        
class MemberForm(forms.ModelForm):
    photo_data = forms.CharField(widget=forms.HiddenInput(), required=False)
    
    class Meta:
        model = Member
        fields = ['name', 'phone_number', 'details']
