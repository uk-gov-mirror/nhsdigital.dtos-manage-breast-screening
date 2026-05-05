from datetime import datetime
from datetime import timezone as tz

import pytest
import time_machine

from manage_breast_screening.dicom.models import Study
from manage_breast_screening.dicom.tests.factories import (
    ReadingSessionItemFactory,
    StudyFactory,
)
from manage_breast_screening.reading.services.reading_session_service import (
    NoImagesToRead,
    ReadingSessionService,
)


@pytest.mark.django_db
class TestSessionService:
    @pytest.fixture
    def older_study(self, current_provider):
        with time_machine.travel(datetime(2026, 1, 1, 9, 0, 0, tzinfo=tz.utc)):
            return StudyFactory.create(
                appointment__clinic_slot__clinic__setting__provider=current_provider,
            )

    @pytest.fixture
    def newer_study(self, current_provider):
        with time_machine.travel(datetime(2026, 1, 1, 10, 0, 0, tzinfo=tz.utc)):
            return StudyFactory.create(
                appointment__clinic_slot__clinic__setting__provider=current_provider,
            )

    def test_create_with_one_study(self, user, current_provider):
        assert Study.objects.count() == 0
        study = StudyFactory.create(
            appointment__clinic_slot__clinic__setting__provider=current_provider,
        )

        item = ReadingSessionService(
            user, current_provider
        ).assign_item_to_new_session()

        assert item.study == study
        assert item.session.items.count() == 1

    def test_create_with_zero_studies(self, user, current_provider):
        with pytest.raises(NoImagesToRead):
            ReadingSessionService(user, current_provider).assign_item_to_new_session()

    def test_create_with_many_studies(
        self, user, current_provider, older_study, newer_study
    ):
        item = ReadingSessionService(
            user, current_provider
        ).assign_item_to_new_session()
        assert item.study == older_study

    def test_create_excludes_studies_already_assigned_to_me(
        self, user, current_provider, older_study, newer_study
    ):
        """
        A study could be assigned to another session, in which case we should ignore it when starting a new session.
        """
        ReadingSessionItemFactory.create(
            case=older_study.cases.first(), session__reader=user
        )

        item = ReadingSessionService(
            user, current_provider
        ).assign_item_to_new_session()
        assert item.study == newer_study

    def test_create_includes_studies_with_one_case_assigned(
        self, user, current_provider, older_study, newer_study
    ):
        ReadingSessionItemFactory(case=older_study.cases.first())

        item = ReadingSessionService(
            user, current_provider
        ).assign_item_to_new_session()
        assert item.study == older_study

    def test_create_excludes_studies_with_all_cases_assigned(
        self, user, current_provider, older_study, newer_study
    ):
        ReadingSessionItemFactory(case=older_study.cases.first())
        ReadingSessionItemFactory(case=older_study.cases.last())

        item = ReadingSessionService(
            user, current_provider
        ).assign_item_to_new_session()
        assert item.study == newer_study


#
