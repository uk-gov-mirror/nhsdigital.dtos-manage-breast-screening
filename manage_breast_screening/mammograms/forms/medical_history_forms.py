from django import forms
from django.forms.widgets import Textarea

from manage_breast_screening.nhsuk_forms.fields import (
    CharField,
    ChoiceField,
)
from manage_breast_screening.participants.models.implanted_medical_device_history_item import (
    ImplantedMedicalDeviceHistoryItem,
)


class ImplantedMedicalDeviceForm(forms.Form):
    def __init__(self, *args, participant, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["symptom_sub_type"] = ChoiceField(
            choices=ImplantedMedicalDeviceHistoryItem.Device,
            label=f"What device does {participant.full_name} have?",
            error_messages={"required": "Select how the skin has changed"},
        )
        self.fields["symptom_sub_type_details"] = CharField(
            required=False,
            label="Describe the change",
            error_messages={"required": "Enter a description of the change"},
            classes="nhsuk-u-width-two-thirds",
        )
        self.fields["additional_information"] = CharField(
            required=False,
            label="Additional info (optional)",
            label_classes="nhsuk-label--m",
            widget=Textarea(attrs={"rows": 4}),
            max_words=500,
            error_messages={
                "max_words": "Additional details must be 500 words or less"
            },
        )

    def initial_values(self, instance):
        return {
            "symptom_sub_type": instance.symptom_sub_type_id,
            "symptom_sub_type_details": instance.symptom_sub_type_details,
        }

    def save(self):
        pass
