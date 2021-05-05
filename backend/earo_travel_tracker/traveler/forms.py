"""
Forms for the traveler app are defined in this file.
"""
from django import forms
from django.utils import timezone
# third party imports
from tempus_dominus.widgets import DatePicker
# earo_travel_tracker imports
from .models import TravelerProfile, ApprovalDelegation


class TravelerBioForm(forms.ModelForm):
    """
    This class defines the ModelForm for the traveler bio from the TravelerDetails Model.
    """
    class Meta:
        model = TravelerProfile
        fields = [
            "department",
            "type_of_traveler",
            "nationality",
            "country_of_duty",
            "contact_telephone",
            "is_managed_by",
            "approver",
        ]


class ApprovalDelegationForm(forms.ModelForm):
    """Model form to delegate approval"""

    class Meta:
        model = ApprovalDelegation
        fields = ['delegate', 'reason_for_delegation', 'start_date', 'end_date']
        widgets = {
            'start_date': DatePicker(attrs={
                            'append': 'fa fa-calendar',
                            }
                        ),
            'end_date': DatePicker(attrs={
                            'append': 'fa fa-calendar',
                            }
                        ),
            'reason_for_delegation': forms.Textarea(attrs={
                            'cols': 80, 'rows': 5, 'style':'resize: none;'
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
        if start_date < timezone.now().date():
            msg = "Delegation cannot begin in the past."
            self.add_error('start_date', msg)
        if start_date and end_date and start_date > end_date:
            msg ="The delegation end date cannot be earlier than the start date."
            self.add_error('end_date', msg)
        return cleaned_data


class ApprovalDelegationRevocationForm(forms.ModelForm):
    """For to revoke approval"""

    class Meta:
        model = ApprovalDelegation
        fields = ["reason_for_revocation"]
        widgets = {
            "reason_for_revocation": forms.Textarea(attrs={
                    'cols': 80, 'rows': 5, 'style':'resize: none;'
                    }
            ),
        }
