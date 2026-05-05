import logging

from django import forms

from manage_breast_screening.batches.services import create_batch_from_csv

logger = logging.getLogger(__name__)


class BatchForm(forms.Form):
    csv_file = forms.FileField(
        error_messages={
            "required": "Select a CSV file to upload",
        },
    )

    def save(self):
        batch_csv = self.cleaned_data["csv_file"]
        create_batch_from_csv(batch_csv)
