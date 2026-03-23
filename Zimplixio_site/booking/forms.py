from django import forms
from .models import BookingRequest


class BookingForm(forms.ModelForm):
    class Meta:
        model = BookingRequest
        fields = ['name', 'email', 'company', 'requested_date', 'requested_time', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'Your full name',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'you@company.com',
            }),
            'company': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'Company name (optional)',
            }),
            'requested_date': forms.HiddenInput(),
            'requested_time': forms.HiddenInput(),
            'message': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': "Anything you'd like us to know before the call? (optional)",
                'rows': 4,
            }),
        }

    def __init__(self, *args, available_times=None, **kwargs):
        super().__init__(*args, **kwargs)
