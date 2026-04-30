import io
import os
from unittest.mock import MagicMock, patch

import pydicom
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from ninja.testing import TestClient
from pydicom.uid import generate_uid

from manage_breast_screening.core.api import api
from manage_breast_screening.gateway.models import GatewayActionStatus
from manage_breast_screening.gateway.tests.factories import (
    GatewayActionFactory,
    GatewayFactory,
)
from manage_breast_screening.participants.models.appointment import (
    AppointmentStatusNames,
)
from manage_breast_screening.participants.tests.factories import AppointmentFactory

from ..authentication import Authentication
from ..authorisation import Authorisation
from ..dicom_recorder import DicomRecorder
from ..models import Study

os.environ["NINJA_SKIP_REGISTRY"] = "yes"

client = TestClient(api)


@pytest.fixture(autouse=True)
def setup(monkeypatch):
    monkeypatch.setenv("API_ENABLED", "true")
    monkeypatch.setenv("API_AUDIENCE", "test_audience")
    monkeypatch.setenv("TENANT_ID", "test_tenant_id")


@pytest.fixture
def dicom_file(dataset) -> bytes:
    with io.BytesIO() as buffer:
        pydicom.dcmwrite(buffer, dataset, enforce_file_format=True)
        buffer.seek(0)
        return SimpleUploadedFile(
            "temp.dcm", buffer.read(), content_type="application/dicom"
        )


@pytest.fixture
def appointment_stub():
    return AppointmentFactory.stub(
        is_in_progress=MagicMock(return_value=True),
    )


@pytest.fixture
def source_message_id():
    return "00000000-0000-0000-0000-000000000009"


@pytest.fixture
def gateway_oid():
    return "00000000-0000-0000-0000-000000000001"


@pytest.fixture
def gateway_action(source_message_id, gateway_oid):
    return GatewayActionFactory(
        id=source_message_id,
        status=GatewayActionStatus.SENT,
        gateway=GatewayFactory(oid=gateway_oid),
    )


@pytest.fixture
def mock_authentication(gateway_oid):
    with patch.object(
        Authentication, "_decode", return_value={"oid": gateway_oid, "sub": "testuser"}
    ):
        yield


@pytest.fixture
def mock_authorisation(gateway_oid):
    with patch.object(Authorisation, "authorise", return_value=True):
        yield


@pytest.mark.django_db
def test_upload_success(dataset, dicom_file, mock_authentication, gateway_action):
    appointment = AppointmentFactory(current_status=AppointmentStatusNames.IN_PROGRESS)

    with patch(
        "manage_breast_screening.dicom.dicom_recorder.lookup_appointment",
        return_value=appointment,
    ):
        response = client.put(
            f"/dicom/{gateway_action.id}",
            FILES={"file": dicom_file},
            headers={"Authorization": "Bearer testtoken"},
        )

        print(response.json())
        assert response.status_code == 201
        json = response.json()
        study = Study.objects.last()
        assert json["study_instance_uid"] == dataset.StudyInstanceUID
        assert json["series_instance_uid"] == dataset.SeriesInstanceUID
        assert json["sop_instance_uid"] == dataset.SOPInstanceUID
        assert json["instance_id"] == str(study.images().first().id)
        assert study.source_message_id == str(gateway_action.id)


def test_upload_no_file(mock_authentication):
    response = client.put(
        "/dicom/abc123",
        FILES={"file": None},
        headers={"Authorization": "Bearer testtoken"},
    )

    assert response.status_code == 422


def test_upload_invalid_file(
    mock_authentication, mock_authorisation, appointment_stub, source_message_id
):
    invalid_file = SimpleUploadedFile(
        "invalid.dcm", b"not a dicom file", content_type="application/dicom"
    )

    with patch(
        "manage_breast_screening.dicom.dicom_recorder.lookup_appointment",
        return_value=appointment_stub,
    ):
        response = client.put(
            f"/dicom/{source_message_id}",
            FILES={"file": invalid_file},
            headers={"Authorization": "Bearer testtoken"},
        )

    assert response.status_code == 400
    assert response.json()["title"] == "Invalid DICOM file"
    assert response.json()["status"] == 400
    assert response.json()["detail"] == "The uploaded file is not a valid DICOM file."


def test_upload_file_thats_too_large(mock_authentication):
    invalid_file = MagicMock(spec=SimpleUploadedFile, size=101 * 1024 * 1024)

    response = client.put(
        "/dicom/abc123",
        FILES={"file": invalid_file},
        headers={"Authorization": "Bearer testtoken"},
    )

    assert response.status_code == 400
    assert response.json()["title"] == "File too large"
    assert response.json()["status"] == 400
    assert response.json()["detail"] == "The file cannot be larger than 100MB"


def test_upload_missing_uids(
    dataset, mock_authentication, mock_authorisation, appointment_stub
):
    del dataset.StudyInstanceUID
    del dataset.SeriesInstanceUID
    del dataset.SOPInstanceUID

    with io.BytesIO() as buffer:
        pydicom.dcmwrite(buffer, dataset, enforce_file_format=True)
        buffer.seek(0)
        dicom_file = SimpleUploadedFile(
            "temp.dcm", buffer.read(), content_type="application/dicom"
        )

    with patch(
        "manage_breast_screening.dicom.dicom_recorder.lookup_appointment",
        return_value=appointment_stub,
    ):
        response = client.put(
            "/dicom/abc123",
            FILES={"file": dicom_file},
            headers={"Authorization": "Bearer testtoken"},
        )

    assert response.status_code == 400
    assert response.json()["title"] == "Missing DICOM attributes"
    assert response.json()["status"] == 400
    assert (
        response.json()["detail"]
        == "The DICOM file is missing required UID attributes."
    )


def test_upload_appointment_not_in_progress(
    dicom_file, mock_authentication, mock_authorisation, appointment_stub
):
    appointment_stub.is_in_progress.return_value = False

    with patch(
        "manage_breast_screening.dicom.dicom_recorder.lookup_appointment",
        return_value=appointment_stub,
    ):
        response = client.put(
            "/dicom/abc123",
            FILES={"file": dicom_file},
            headers={"Authorization": "Bearer testtoken"},
        )

        assert response.status_code == 500
        assert response.json()["title"] == "Internal Server Error"


def test_upload_when_api_disabled(dicom_file, mock_authentication, monkeypatch):
    monkeypatch.setenv("API_ENABLED", "false")

    response = client.put(
        "/dicom/abc123",
        FILES={"file": dicom_file},
        headers={"Authorization": "Bearer testtoken"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "API is not available"


def test_upload_no_auth(dicom_file):
    response = client.put(
        "/dicom/abc123",
        FILES={"file": dicom_file},
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Unauthorized",
    }


def test_upload_invalid_auth(dicom_file):
    response = client.put(
        "/dicom/abc123",
        FILES={"file": dicom_file},
        headers={"Authorization": "Bearer invalidtoken"},
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Unauthorized",
    }


@patch.object(Authentication, "bypass_authentication", return_value=True)
@patch.object(Authorisation, "bypass_authorisation", return_value=True)
def test_upload_bypass_auth(_y, _x, dicom_file):
    with patch.object(
        DicomRecorder,
        "get_or_create_records",
        return_value=(
            MagicMock(study_instance_uid=generate_uid()),
            MagicMock(series_instance_uid=generate_uid()),
            MagicMock(sop_instance_uid=generate_uid(), id=1),
        ),
    ):
        response = client.put(
            "/dicom/abc123",
            FILES={"file": dicom_file},
            headers={"Authorization": "Bearer anytoken"},
        )

    assert response.status_code == 201


@pytest.mark.django_db
def test_report_failure(mock_authentication):
    action = GatewayActionFactory()

    response = client.patch(
        f"/dicom/{action.id}/failure",
        json={"error": "Missing PatientID"},
        headers={"Authorization": "Bearer testtoken"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "failure recorded"

    action.refresh_from_db()
    assert action.status == GatewayActionStatus.IMAGE_FAILED
    assert action.last_error == "Missing PatientID"
    assert action.failed_at is not None


@pytest.mark.django_db
def test_report_failure_action_not_found(mock_authentication):
    response = client.patch(
        "/dicom/00000000-0000-0000-0000-000000000000/failure",
        json={"error": "Missing PatientID"},
        headers={"Authorization": "Bearer testtoken"},
    )

    assert response.status_code == 404
    assert response.json()["title"] == "Not Found"
