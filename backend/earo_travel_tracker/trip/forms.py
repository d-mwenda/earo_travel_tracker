"""
Forms for the trip app are defined in this file.
"""
from django import forms
# third-party library imports
from tempus_dominus.widgets import DatePicker, TimePicker
# earo_travel_tracker imports
from .models import Trip, TripApproval, TripItinerary


class TripForm(forms.ModelForm):
    """
    This class defines the ModelForm for the Trip model.
    """
    class Meta:
        model = Trip
        fields = [
                'trip_name',
                'type_of_travel',
                'category_of_travel',
                'reason_for_travel',
                'start_date',
                'end_date',
                'is_mission_critical',
                'security_level',
                'scope_of_work',
                ]

        widgets = {
            'reason_for_travel': forms.Textarea(
                                            attrs={'cols': 80, 'rows': 5, 'style':'resize: none;'}
                                            ),
            'is_mission_critical': forms.Select(choices=(
                                                        ('True', 'Yes'),
                                                        ('False', 'No')
                                                        )
                                                ),
            'start_date': DatePicker(attrs={
                                    'append': 'fa fa-calendar',
                                    'input_toggle': False,
                                    }
                            ),
            'end_date': DatePicker(attrs={
                                    'append': 'fa fa-calendar',
                                    }
                            ),
        }

    def clean(self):
        """
        Check that the supplied trip dates are logical.
        """
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        if start_date and end_date and start_date > end_date:
            msg ="The trip end date cannot be earlier than the trip start date."
            self.add_error('end_date', msg)
        return cleaned_data


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
            'approval_comment': forms.Textarea(attrs={
                    'cols': 80, 'rows': 5, 'style':'resize: none;'
                    }),
        }


class TripItineraryForm(forms.ModelForm):
    """
    This class defines the modelform used to create and edit trip itinerary.
    The trip is excluded from the form as the UI design is such that the form view will always be
    referred to by a trip view.
    """

    class Meta:
        model = TripItinerary
        fields = [
            'date_of_departure',
            'time_of_departure',
            'city_of_departure',
            'destination',
            'mode_of_travel',
            'comment',
        ]
        widgets = {
            'date_of_departure': DatePicker(attrs={
                                    'append': 'fa fa-calendar',
                                    }
            ),
            'time_of_departure': TimePicker(
                                    options={
                                        'format': 'HH:mm',
                                        'useCurrent': False,
                                    },
                                    attrs={
                                        'append': 'fa fa-clock',
                                        }
                                )
        }
