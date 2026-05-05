from unittest.mock import MagicMock, patch

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from manage_breast_screening.batches.forms import BatchForm


@pytest.mark.django_db
@patch(
    "manage_breast_screening.batches.forms.create_batch_from_csv",
    return_value=MagicMock(),
)
class TestBatchForm:
    def test_save_with_a_file(self, mock_create_batch_from_csv):
        lines = [
            "Row",
            "1",
        ]

        csv_content = ("\n".join(lines)).encode("utf-8")
        csv_file = SimpleUploadedFile(
            "batches.csv", csv_content, content_type="text/csv"
        )

        form = BatchForm(
            data={"csv_file": csv_file},
            files={"csv_file": csv_file},
        )
        assert form.is_valid()
        form.save()
        mock_create_batch_from_csv.assert_called_with(csv_file)

    def test_no_file_provided(self, _):
        form = BatchForm(
            data={"csv_file": None},
            files={"csv_file": None},
        )
        assert form.is_valid() is False
