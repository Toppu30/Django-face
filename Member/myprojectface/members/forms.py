# members/forms.py

from django import forms
from .models import Member

class MemberForm(forms.ModelForm):
    photo_data = forms.CharField(widget=forms.HiddenInput(), required=False)
    
    class Meta:
        model = Member
        fields = ['name', 'phone_number', 'details']
