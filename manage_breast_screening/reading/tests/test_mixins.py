import pytest
from django.http import Http404, HttpResponse
from django.test import RequestFactory
from django.views import View

from manage_breast_screening.clinics.tests.factories import ProviderFactory
from manage_breast_screening.dicom.tests.factories import (
    ReadingSessionFactory,
    ReadingSessionItemFactory,
    StudyFactory,
)
from manage_breast_screening.participants.tests.factories import AppointmentFactory
from manage_breast_screening.reading.mixins import ReadingMixin
from manage_breast_screening.users.tests.factories import UserFactory


@pytest.mark.django_db
class TestReadingMixin:
    class DummyView(ReadingMixin, View):
        def get(self, request, pk, **kwargs):
            return HttpResponse(status=200)

    class TestReadingSessionItem:
        @pytest.fixture
        def provider(self):
            return ProviderFactory.create()

        @pytest.fixture
        def reader(self, provider):
            user = UserFactory.create()
            user.current_provider = provider
            return user

        @pytest.fixture
        def item(self, provider):
            appointment = AppointmentFactory(
                clinic_slot__clinic__setting__provider=provider
            )
            study = StudyFactory(appointment=appointment)
            session = ReadingSessionFactory()
            return ReadingSessionItemFactory(session=session, study=study)

        def test_returns_item_for_current_provider(self, reader, item):
            request = RequestFactory().get("/")
            request.user = reader

            view = TestReadingMixin.DummyView()
            view.request = request
            view.kwargs = {"pk": item.pk}

            assert view.reading_session_item == item

        def test_raises_404_for_other_provider(self, reader, item):
            other_provider = ProviderFactory.create()
            reader.current_provider = other_provider

            request = RequestFactory().get("/")
            request.user = reader

            view = TestReadingMixin.DummyView()
            view.request = request
            view.kwargs = {"pk": item.pk}

            with pytest.raises(Http404):
                view.reading_session_item  # noqa: B018
