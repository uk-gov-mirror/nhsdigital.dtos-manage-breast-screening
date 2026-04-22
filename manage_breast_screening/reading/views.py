from django.forms import Form
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.views.generic import FormView
from rules.contrib.views import PermissionRequiredMixin

from manage_breast_screening.auth.models import Permission
from manage_breast_screening.mammograms.presenters.medical_history.check_medical_information_presenter import (
    CheckMedicalInformationPresenter,
)
from manage_breast_screening.mammograms.views.mixins import AppointmentMixin


@require_http_methods(["GET"])
def show_reading_dashboard_view(request):
    return render(request, "show_readings.jinja")


class ReadImageView(PermissionRequiredMixin, AppointmentMixin, FormView):
    form_class = Form
    template_name = "read_image.jinja"
    permission_required = Permission.VIEW_MAMMOGRAM_APPOINTMENT

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        images = []

        context.update(
            {
                "heading": self.participant.full_name,
                "caption": "Review images",
                "images": images,
                "presented_medical_information": CheckMedicalInformationPresenter(
                    self.appointment
                ),
                "notes_for_reader": self.appointment.study.additional_details,
                "is_urgent": True,
                "is_second_read": True,
                "is_previously_skipped": True,
                "previous_case": True,
            },
        )

        return context

    def _get_images(self, study):
        images = []

        for series in study.series.all():
            for image in series.images.all():
                images.append(
                    {
                        "name": image.laterality_and_view,
                        "url": image.image_file.url,
                        "class": "app-mammogram-thumbnail--"
                        + ("right" if series.laterality == "R" else "left"),
                    }
                )

        return images
