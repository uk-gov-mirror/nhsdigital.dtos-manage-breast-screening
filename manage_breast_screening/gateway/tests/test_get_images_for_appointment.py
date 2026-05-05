from unittest.mock import patch

import pytest
from pydicom.uid import generate_uid
from pytest_django.asserts import assertQuerySetEqual

from manage_breast_screening.dicom.models import Image, Series, Study
from manage_breast_screening.gateway.relay_service import RelayService
from manage_breast_screening.gateway.tests.factories import RelayFactory
from manage_breast_screening.gateway.worklist_item_service import (
    WorklistItemService,
    get_images_for_appointment,
)
from manage_breast_screening.participants.tests.factories import AppointmentFactory


@patch.object(RelayService, "send_action")
@pytest.mark.django_db
class TestGetImagesForAppointment:
    def test_returns_empty_queryset_when_no_relay(self, _):
        appointment = AppointmentFactory()

        WorklistItemService.create(appointment)

        images = get_images_for_appointment(appointment)

        assert not images.exists()

    def test_returns_empty_queryset_when_no_gateway_action(self, _):
        appointment = AppointmentFactory()
        RelayFactory(setting=appointment.clinic_slot.clinic.setting)

        images = get_images_for_appointment(appointment)

        assert not images.exists()

    def test_returns_empty_queryset_when_no_series(self, _):
        appointment = AppointmentFactory()
        RelayFactory(setting=appointment.clinic_slot.clinic.setting)

        action = WorklistItemService.create(appointment)

        Study.objects.create(
            study_instance_uid=generate_uid(),
            source_message_id=str(action.id),
            appointment=appointment,
        )

        images = get_images_for_appointment(appointment)

        assert not images.exists()

    def test_returns_empty_queryset_when_no_images_in_series(self, _):
        appointment = AppointmentFactory()
        RelayFactory(setting=appointment.clinic_slot.clinic.setting)

        action = WorklistItemService.create(appointment)

        study = Study.objects.create(
            study_instance_uid=generate_uid(),
            source_message_id=str(action.id),
            appointment=appointment,
        )
        Series.objects.create(
            study=study,
            series_instance_uid=generate_uid(),
        )

        images = get_images_for_appointment(appointment)

        assert not images.exists()

    def test_returns_empty_queryset_when_no_images(self, _):
        appointment = AppointmentFactory()
        RelayFactory(setting=appointment.clinic_slot.clinic.setting)

        WorklistItemService.create(appointment)

        images = get_images_for_appointment(appointment)

        assert not images.exists()

    def test_returns_images_linked_to_appointment(self, _):
        appointment = AppointmentFactory()
        RelayFactory(setting=appointment.clinic_slot.clinic.setting)

        action = WorklistItemService.create(appointment)

        study = Study.objects.create(
            study_instance_uid=generate_uid(),
            source_message_id=str(action.id),
            appointment=appointment,
        )
        series = Series.objects.create(
            study=study,
            series_instance_uid=generate_uid(),
        )
        image = Image.objects.create(
            series=series,
            sop_instance_uid=generate_uid(),
        )

        images = get_images_for_appointment(appointment)

        assertQuerySetEqual(images, [image])
