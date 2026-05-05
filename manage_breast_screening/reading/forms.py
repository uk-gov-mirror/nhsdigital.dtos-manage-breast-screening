from django import forms
from django.forms import widgets

from manage_breast_screening.nhsuk_forms.fields.boolean_field import (
    BooleanField,
)
from manage_breast_screening.nhsuk_forms.fields.char_field import CharField
from manage_breast_screening.nhsuk_forms.fields.choice_fields import ChoiceField
from manage_breast_screening.nhsuk_forms.forms import FormWithConditionalFields

VIEWS = ["rcc", "rmlo", "lcc", "lmlo"]

RECALL_REASON_CHOICES = [
    ("", "Select a reason"),
    ("breast_positioning", "Breast positioning"),
    ("incorrect_exposure", "Incorrect exposure"),
    ("image_obscured", "Image obscured"),
    ("image_blurred", "Image blurred"),
    ("image_missing", "Image missing"),
    ("other_reason", "Other reason"),
]


class TechnicalRecallForm(FormWithConditionalFields):
    rcc = BooleanField(required=False, label="RCC")
    rcc_reason = ChoiceField(
        widget=widgets.Select,
        choices=RECALL_REASON_CHOICES,
        label="Reason for recall",
        required=False,
        error_messages={"required": "Select a reason for recall"},
    )
    rcc_details = CharField(required=False, label="Additional details (optional)")

    rmlo = BooleanField(required=False, label="RMLO")
    rmlo_reason = ChoiceField(
        widget=widgets.Select,
        choices=RECALL_REASON_CHOICES,
        label="Reason for recall",
        required=False,
        error_messages={"required": "Select a reason for recall"},
    )
    rmlo_details = CharField(required=False, label="Additional details (optional)")

    lcc = BooleanField(required=False, label="LCC")
    lcc_reason = ChoiceField(
        widget=widgets.Select,
        choices=RECALL_REASON_CHOICES,
        label="Reason for recall",
        required=False,
        error_messages={"required": "Select a reason for recall"},
    )
    lcc_details = CharField(required=False, label="Additional details (optional)")

    lmlo = BooleanField(required=False, label="LMLO")
    lmlo_reason = ChoiceField(
        widget=widgets.Select,
        choices=RECALL_REASON_CHOICES,
        label="Reason for recall",
        required=False,
        error_messages={"required": "Select a reason for recall"},
    )
    lmlo_details = CharField(required=False, label="Additional details (optional)")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for view in VIEWS:
            self.given_field_value(view, True).require_field(f"{view}_reason")

    def clean(self):
        cleaned_data = super().clean()
        if not any(cleaned_data.get(view) for view in VIEWS):
            raise forms.ValidationError("Select at least one view to retake")
        return cleaned_data
