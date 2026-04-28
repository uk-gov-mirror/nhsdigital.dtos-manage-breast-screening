from logging import getLogger

from django.contrib.auth.decorators import permission_required
from django.forms import Form
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.views.generic import FormView, TemplateView
from rules.contrib.views import PermissionRequiredMixin

from manage_breast_screening.auth.models import Permission
from manage_breast_screening.mammograms.presenters.medical_history.check_medical_information_presenter import (
    CheckMedicalInformationPresenter,
)
from manage_breast_screening.participants.models import Appointment

logger = getLogger(__name__)


@require_http_methods(["GET"])
@permission_required(Permission.READ_IMAGES, raise_exception=True)
def show_reading_dashboard_view(request):
    return render(request, "show_readings.jinja")


class ShowImageReadView(PermissionRequiredMixin, FormView):
    form_class = Form
    template_name = "read_image.jinja"
    permission_required = Permission.READ_IMAGES

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # TODO: dummy data — replace once retrieval of the appropriate Reading object is implemented.
        appointment = Appointment.with_study().first()
        participant = appointment.participant

        images = []

        context.update(
            {
                "heading": participant.full_name,
                "caption": "Review images",
                "images": images,
                "presented_medical_information": CheckMedicalInformationPresenter(
                    appointment
                ),
                "notes_for_reader": appointment.study.additional_details,
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


class AddTechnicalRecallView(TemplateView):
    template_name = "reading/technical_recall.jinja"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "page_title": "Technical recall",
                "back_link_params": {"href": "#"},
            }
        )
        return context
