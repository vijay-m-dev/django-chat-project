from django import forms
from .models import GroupChat


class GroupForm(forms.ModelForm):
	class Meta:
		model = GroupChat
		fields = ['name']
