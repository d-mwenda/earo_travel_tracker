"""
Forms for the trip app are defined in this file.
"""
from django import forms
# earo_travel_tracker imports
from .models import Trips


class TripForm(forms.ModelForm):
    """
    This class defines the ModelForm for the Trip model.
    """
    class Meta:
        model = Trips
        exclude = ['created_on', 'is_travel_completed']
        widgets = {
            'reason_for_travel': forms.Textarea(attrs={'cols': 80, 'rows': 5, 'style':'resize: none;'}),
            'is_mission_critical': forms.Select(choices=(
                ('True', 'Yes'),
                ('False', 'No')
            ))
        }

    def __init__(self, *args, **kwargs):
        super(TripForm, self).__init__(*args, **kwargs)
        self.fields['start_date'].widget.attrs.update({
            'placeholder': 'YYYY-MM-DD',
        })
        self.fields['end_date'].widget.attrs.update({
            'placeholder': 'YYYY-MM-DD',
        })
