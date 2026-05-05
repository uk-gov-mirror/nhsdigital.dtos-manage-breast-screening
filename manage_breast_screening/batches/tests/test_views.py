import pytest
from django.contrib import messages
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from pytest_django.asserts import assertInHTML, assertMessages

from manage_breast_screening.batches.tests.factories import BatchFactory


@pytest.mark.django_db
class TestBatchCsvUploadView:
    @pytest.fixture(autouse=True)
    def enable_flag(self, with_flag_enabled):
        with_flag_enabled("batches")

    def test_renders_response(self, administrative_user_client):
        response = administrative_user_client.http.get(
            reverse(
                "batches:upload_csv",
            )
        )
        assert response.status_code == 200

    def test_get_with_flag_disabled_errors(
        self, with_flag_disabled, administrative_user_client
    ):
        with_flag_disabled("batches")
        response = administrative_user_client.http.get(
            reverse(
                "batches:upload_csv",
            )
        )
        assert response.status_code == 404

    def test_missing_data_produces_validation_error(self, administrative_user_client):
        response = administrative_user_client.http.post(
            reverse(
                "batches:upload_csv",
            )
        )
        assert response.status_code == 200

        assertInHTML(
            """
                <ul class="nhsuk-list nhsuk-error-summary__list">
                    <li><a href="#id_csv_file">Select a CSV file to upload</a></li>
                </ul>
            """,
            response.text,
        )

    def test_invalid_post_throws_error(self, administrative_user_client):
        lines = [
            "Row,NHS Number,Surname",
            "1,999 999 9991,SMITH",
        ]

        csv_content = ("\n".join(lines)).encode("utf-8")
        uploaded_file = SimpleUploadedFile(
            "batches.csv", csv_content, content_type="text/csv"
        )
        response = administrative_user_client.http.post(
            reverse(
                "batches:upload_csv",
            ),
            {"csv_file": uploaded_file},
        )
        assertMessages(
            response,
            [
                messages.Message(
                    level=messages.INFO,
                    message="Batch upload failed.",
                )
            ],
        )

    def test_post_with_valid_data_succeeds(self, administrative_user_client):
        lines = [
            "Batch Parameters",
            "BSO Batch ID,BS1345815F",
            "Batch Title,Batch title 1",
        ]

        csv_content = ("\n".join(lines)).encode("utf-8")

        csv_file = SimpleUploadedFile(
            "batches.csv", csv_content, content_type="text/csv"
        )
        response = administrative_user_client.http.post(
            reverse(
                "batches:upload_csv",
            ),
            {"csv_file": csv_file},
        )
        assertMessages(
            response,
            [
                messages.Message(
                    level=messages.SUCCESS,
                    message="Batch uploaded successfully.",
                )
            ],
        )

    def test_post_with_same_id_throws_error(self, administrative_user_client):
        _existing_batch = BatchFactory.create(bso_batch_id="BS1345815F")

        lines = [
            "Batch Parameters",
            "BSO Batch ID,BS1345815F",
            "Batch Title,Batch title 1",
        ]

        csv_content = ("\n".join(lines)).encode("utf-8")

        csv_file = SimpleUploadedFile(
            "batches.csv", csv_content, content_type="text/csv"
        )
        response = administrative_user_client.http.post(
            reverse(
                "batches:upload_csv",
            ),
            {"csv_file": csv_file},
        )
        assertMessages(
            response,
            [
                messages.Message(
                    level=messages.INFO,
                    message="Batch upload failed.",
                )
            ],
        )


@pytest.mark.django_db
class TestBatchIndexView:
    @pytest.fixture(autouse=True)
    def enable_flag(self, with_flag_enabled):
        with_flag_enabled("batches")

    def test_renders_no_batches(self, administrative_user_client):
        response = administrative_user_client.http.get(
            reverse(
                "batches:index",
            )
        )
        assert response.status_code == 200
        assert "No batches found." in response.text

    def test_renders_with_batches(self, administrative_user_client):
        _existing_batch = BatchFactory.create(title="Batch title 1")
        response = administrative_user_client.http.get(
            reverse(
                "batches:index",
            )
        )
        assert "Batch title 1" in response.text

    def test_get_with_flag_disabled_errors(
        self, with_flag_disabled, administrative_user_client
    ):
        with_flag_disabled("batches")
        response = administrative_user_client.http.get(
            reverse(
                "batches:index",
            )
        )
        assert response.status_code == 404
