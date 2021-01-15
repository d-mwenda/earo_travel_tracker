"""
Forms for the traveler app are defined in this file.
"""
from django import forms
# earo_travel_tracker imports
from .models import TravelerProfile


class TravelerBioForm(forms.ModelForm):
    """
    This class defines the ModelForm for the traveler bio from the TravelerDetails Model.
    """
    class Meta:
        model = TravelerProfile
        fields = '__all__'

    # def __init__(self, *args, **kwargs):
    #     super(TravelerBioForm, self).__init__(*args, **kwargs)
    #     self.fields['date_of_birth'].widget.attrs.update({
    #         'placeholder': 'YYYY-MM-DD',
    #     })
