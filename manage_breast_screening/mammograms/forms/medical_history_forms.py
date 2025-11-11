from django import forms
from django.db.models import TextChoices
from django.forms import CheckboxSelectMultiple
from django.forms.widgets import Textarea

from manage_breast_screening.nhsuk_forms.fields import (
    CharField,
    ChoiceField,
)
from manage_breast_screening.nhsuk_forms.fields.choice_fields import (
    MultipleChoiceField,
)
from manage_breast_screening.participants.models.implanted_medical_device_history_item import (
    ImplantedMedicalDeviceHistoryItem,
)


class HasBeenRemovedChoices(TextChoices):
    HAS_BEEN_REMOVED = "HAS_BEEN_REMOVED", "Implanted device has been removed"


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
            hint="Leave blank if unknown",
            required=False,
            label="Year of procedure (optional)",
            label_classes="nhsuk-label--m",
            classes="nhsuk-u-width-two-thirds",
        )
        self.fields["is_removed"] = MultipleChoiceField(
            choices=HasBeenRemovedChoices,
            widget=CheckboxSelectMultiple,
            label="Removed implants",
            error_messages={"required": "Select which nipples have changed"},
            classes="app-checkboxes",
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
