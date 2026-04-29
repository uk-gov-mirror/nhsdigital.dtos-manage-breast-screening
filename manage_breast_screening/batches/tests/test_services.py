import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from manage_breast_screening.batches.models import Batch
from manage_breast_screening.batches.services import create_batch_from_csv


class TestCreateBatchFromCsv:
    @pytest.mark.django_db
    def test_valid_csv(self):
        lines = [
            "Batch Parameters",
            "BSO Batch ID,BS1345815F",
            "Batch Title,Batch title 1",
        ]

        csv_content = ("\n".join(lines)).encode("utf-8")

        csv_file = SimpleUploadedFile(
            "batches.csv", csv_content, content_type="text/csv"
        )
        batch = create_batch_from_csv(csv_file)
        assert batch.bso_batch_id == "BS1345815F"
        assert batch.title == "Batch title 1"

    @pytest.mark.django_db
    def test_not_csv_raises_exception(self):
        invalid_csv_content = "This is not a valid CSV file."
        assert Batch.objects.count() == 0
        with pytest.raises(Exception):
            create_batch_from_csv(invalid_csv_content)

        assert Batch.objects.count() == 0

    @pytest.mark.django_db
    def test_invalid_csv_raises_exception(self):
        lines = [
            "SomeOther Heading",
            "BSO Batch ID,BS1345815F",
            "Batch Title,Batch title 1",
        ]

        csv_content = ("\n".join(lines)).encode("utf-8")
        assert Batch.objects.count() == 0
        with pytest.raises(Exception):
            create_batch_from_csv(csv_content)

        assert Batch.objects.count() == 0
