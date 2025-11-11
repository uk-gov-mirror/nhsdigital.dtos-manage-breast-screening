from django import forms
from django.forms.widgets import Textarea

from manage_breast_screening.nhsuk_forms.fields import (
    BooleanField,
    CharField,
    ChoiceField,
)
from manage_breast_screening.participants.models.implanted_medical_device_history_item import (
    ImplantedMedicalDeviceHistoryItem,
)


class ImplantedMedicalDeviceForm(forms.Form):
    def __init__(self, *args, participant, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["device_sub_type"] = ChoiceField(
            choices=ImplantedMedicalDeviceHistoryItem.Device,
            label=f"What device does {participant.full_name} have?",
            error_messages={"required": "Select the device type"},
        )
        self.fields["device_sub_type_details"] = CharField(
            required=False,
            label="Provide details",
            error_messages={"required": "Provide details of the device"},
            classes="nhsuk-u-width-two-thirds",
        )
        self.fields["procedure_year"] = CharField(
            required=False,
            label="Year of procedure (optional)",
            label_classes="nhsuk-label--m",
            classes="nhsuk-u-width-two-thirds",
        )
        self.fields["is_removed"] = BooleanField(
            required=False, label="Implanted device has been removed"
        )
        self.fields["removal_year"] = CharField(
            required=False,
            label="Year removed",
            classes="nhsuk-u-width-two-thirds",
            error_messages={"required": "Implanted device has been removed"},
        )
        self.fields["additional_information"] = CharField(
            required=False,
            label="Additional details (optional)",
            label_classes="nhsuk-label--m",
            widget=Textarea(attrs={"rows": 4}),
            max_words=500,
            error_messages={
                "max_words": "Additional details must be 500 words or less"
            },
        )

    def initial_values(self, instance):
        return {
            "device_sub_type": instance.device_sub_type_id,
            "device_sub_type_details": instance.device_sub_type_details,
        }

    def save(self):
        pass
