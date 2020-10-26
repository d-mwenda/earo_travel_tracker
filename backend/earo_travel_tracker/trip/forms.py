"""
Forms for the trip app are defined in this file.
"""
from django import forms
# earo_travel_tracker imports
from .models import Trips, TripApproval


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
                                                        )
                                                ),
            'traveler': forms.HiddenInput()
        }

    def __init__(self, *args, **kwargs):
        super(TripForm, self).__init__(*args, **kwargs)
        self.fields['start_date'].widget.attrs.update({
            'placeholder': 'YYYY-MM-DD',
        })
        self.fields['end_date'].widget.attrs.update({
            'placeholder': 'YYYY-MM-DD',
        })


class ApprovalRequestForm(forms.Form):
    """
    This form is meant to be a placeholder form to create an approval request once approval request
    button is created.
    """
    placeholder = forms.HiddenInput()


class TripApprovalForm(forms.ModelForm):
    """
    This class defines the form that is presented to the approver to approve a trip request.
    """
    CHOICES = [
        ('0', 'Decline'),
        ('1', 'Approve')
    ]
    trip_is_approved = forms.ChoiceField(choices=CHOICES,label='Approval')
    class Meta:
        model = TripApproval
        fields = ['approval_comment', 'trip_is_approved',]
        widgets = {
            'approval_comment': forms.Textarea(attrs={'cols': 80, 'rows': 5, 'style':'resize: none;'}),
        }

