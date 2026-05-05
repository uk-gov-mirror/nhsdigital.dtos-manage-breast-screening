from urllib.parse import urlencode

import pytest
from django.http import QueryDict

from manage_breast_screening.reading.forms import TechnicalRecallForm


def make_form(data):
    return TechnicalRecallForm(QueryDict(urlencode(data)))


class TestTechnicalRecallForm:
    class TestClean:
        def test_no_views_selected_is_invalid(self):
            form = make_form({})
            assert not form.is_valid()
            assert form.non_field_errors() == ["Select at least one view to retake"]

        @pytest.mark.parametrize("view", ["rcc", "rmlo", "lcc", "lmlo"])
        def test_view_checked_without_reason_is_invalid(self, view):
            form = make_form({view: "true"})
            assert not form.is_valid()
            assert form.errors == {
                f"{view}_reason": [f"Select a reason for the {view.upper()} view"]
            }

        @pytest.mark.parametrize("view", ["rcc", "rmlo", "lcc", "lmlo"])
        def test_view_checked_with_reason_is_valid(self, view):
            form = make_form({view: "true", f"{view}_reason": "breast_positioning"})
            assert form.is_valid()

        def test_multiple_views_checked_missing_reasons_reports_each(self):
            form = make_form({"rcc": "true", "lmlo": "true"})
            assert not form.is_valid()
            assert form.errors == {
                "rcc_reason": ["Select a reason for the RCC view"],
                "lmlo_reason": ["Select a reason for the LMLO view"],
            }

        def test_reason_for_unchecked_view_is_ignored(self):
            form = make_form(
                {
                    "rcc": "true",
                    "rcc_reason": "breast_positioning",
                    "lmlo_reason": "image_blurred",
                }
            )
            assert form.is_valid()
