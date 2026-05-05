from django.urls import reverse
from playwright.sync_api import expect

from manage_breast_screening.auth.models import Role
from manage_breast_screening.dicom.models import Opinions, Reading
from manage_breast_screening.dicom.tests.factories import (
    CaseFactory,
    ReadingSessionFactory,
    ReadingSessionItemFactory,
)
from manage_breast_screening.dicom.tests.factories import (
    StudyFactory as DicomStudyFactory,
)
from manage_breast_screening.participants.models.appointment import (
    AppointmentStatusNames,
)
from manage_breast_screening.participants.tests.factories import AppointmentFactory

from ..system_test_setup import SystemTestCase


class TestReaderSubmitsTechnicalRecall(SystemTestCase):
    def test_reader_submits_technical_recall(self):
        self.given_i_am_logged_in_as_a_reader()
        self.and_there_is_a_reading_session_item_for_me()
        self.when_i_visit_the_reading_session_item_page()
        self.and_i_click_technical_recall()
        self.then_i_see_the_technical_recall_form()

        self.when_i_submit_the_form_without_filling_anything_in()
        self.then_i_see_validation_errors()

        self.when_i_select_views_to_retake()
        self.and_i_submit_the_form()

        # TODO: update this assertion once we have a service that can provide us the next session item to read
        self.then_i_am_on_the_reading_dashboard()
        self.and_a_technical_recall_reading_is_recorded()

    def given_i_am_logged_in_as_a_reader(self):
        self.login_as_role(Role.READER)

    def and_there_is_a_reading_session_item_for_me(self):
        self.appointment = AppointmentFactory(
            clinic_slot__clinic__setting__provider=self.current_provider,
            current_status=AppointmentStatusNames.SCREENED,
        )
        dicom_study = DicomStudyFactory(appointment=self.appointment)
        self.session = ReadingSessionFactory(reader=self.current_user)
        self.item = ReadingSessionItemFactory(
            session=self.session, case=CaseFactory(study=dicom_study)
        )

    def when_i_visit_the_reading_session_item_page(self):
        self.page.goto(
            self.live_server_url
            + reverse(
                "reading:image_read",
                kwargs={"session_pk": self.session.pk, "pk": self.item.pk},
            )
        )

    def and_i_click_technical_recall(self):
        self.page.get_by_role("button", name="Technical recall").click()

    def then_i_see_the_technical_recall_form(self):
        expect(
            self.page.get_by_role("heading", name="Technical recall")
        ).to_be_visible()

    def when_i_submit_the_form_without_filling_anything_in(self):
        self.page.get_by_role("button", name="Continue").click()

    def then_i_see_validation_errors(self):
        expect(self.page.locator(".nhsuk-error-summary")).to_contain_text(
            "Select at least one view to retake"
        )

    def when_i_select_views_to_retake(self):
        self.page.get_by_label("RCC", exact=True).check()
        self.page.locator("#id_rcc_reason").select_option("breast_positioning")
        self.page.get_by_label("LMLO", exact=True).check()
        self.page.locator("#id_lmlo_reason").select_option("image_blurred")

    def and_i_submit_the_form(self):
        self.page.get_by_role("button", name="Continue").click()

    def then_i_am_on_the_reading_dashboard(self):
        self.expect_url("reading:show_reading_dashboard")

    def and_a_technical_recall_reading_is_recorded(self):
        reading = Reading.objects.get(study=self.item.study, reader=self.current_user)
        assert reading.opinion == Opinions.TECHNICAL_RECALL
