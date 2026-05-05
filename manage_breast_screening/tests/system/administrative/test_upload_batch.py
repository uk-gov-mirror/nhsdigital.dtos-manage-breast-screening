from django.urls import reverse
from playwright.sync_api import expect

from ..system_test_setup import SystemTestCase


class TestUploadBatch(SystemTestCase):
    def test_uploading_a_new_batch(self, with_flag_enabled):
        self.given_the_batches_flag_is_enabled(with_flag_enabled)
        self.given_i_am_logged_in_as_an_administrative_user()
        self.and_i_am_on_the_batch_upload_page()
        self.when_i_submit_a_batch_csv()
        self.then_i_see_a_success_message()
        self.and_i_can_see_the_batch_in_the_batch_list()

    def given_the_batches_flag_is_enabled(self, with_flag_enabled):
        with_flag_enabled("batches")

    def and_i_am_on_the_batch_upload_page(self):
        self.page.goto(
            self.live_server_url
            + reverse(
                "batches:upload_csv",
            )
        )

    def when_i_submit_a_batch_csv(self):
        self.page.get_by_test_id("csv-file-input").set_input_files(
            "manage_breast_screening/batches/tests/fixtures/bss_batch.csv"
        )
        self.page.click("text=Save and continue")

    def then_i_see_a_success_message(self):
        expect(
            self.page.locator(".nhsuk-notification-banner__content")
        ).to_contain_text("Batch uploaded successfully")

    def and_i_can_see_the_batch_in_the_batch_list(self):
        expect(self.page.locator("table")).to_contain_text("Batch title 1")
