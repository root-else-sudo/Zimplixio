from django import forms
from .models import BookingRequest


class BookingForm(forms.ModelForm):
    class Meta:
        model = BookingRequest
        fields = ['name', 'email', 'company', 'requested_date', 'requested_time', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'Your full name',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'you@company.com',
            }),
            'company': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'Company name (optional)',
            }),
            'requested_date': forms.DateInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500',
                'type': 'date',
            }),
            'requested_time': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500',
            }),
            'message': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'Anything you\'d like us to know before the call? (optional)',
                'rows': 4,
            }),
        }

    def __init__(self, *args, available_times=None, **kwargs):
        super().__init__(*args, **kwargs)
        if available_times:
            self.fields['requested_time'].widget.choices = [('', 'Select a time')] + [
                (t.strftime('%H:%M'), t.strftime('%I:%M %p')) for t in available_times
            ]
        else:
            self.fields['requested_time'].widget.choices = [('', 'No times available')]
