from logging import getLogger

from django.contrib.auth.decorators import permission_required
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.decorators.http import require_http_methods
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from rules.contrib.views import PermissionRequiredMixin

from manage_breast_screening.auth.models import Permission
from manage_breast_screening.dicom.models import Opinions, Reading
from manage_breast_screening.mammograms.presenters.medical_history.check_medical_information_presenter import (
    CheckMedicalInformationPresenter,
)

from .forms import TechnicalRecallForm
from .mixins import ReadingMixin

logger = getLogger(__name__)


@require_http_methods(["GET"])
@permission_required(Permission.READ_IMAGES, raise_exception=True)
def show_reading_dashboard_view(request):
    return render(request, "show_readings.jinja")


class ShowImageReadView(ReadingMixin, PermissionRequiredMixin, TemplateView):
    template_name = "read_image.jinja"
    permission_required = Permission.READ_IMAGES

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        item = self.reading_session_item
        appointment = item.study.appointment
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
                "notes_for_reader": item.study.additional_details,
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


class AddTechnicalRecallView(ReadingMixin, PermissionRequiredMixin, FormView):
    template_name = "reading/technical_recall.jinja"
    permission_required = Permission.READ_IMAGES
    form_class = TechnicalRecallForm
    success_url = reverse_lazy("reading:show_reading_dashboard")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "page_title": "Technical recall",
                "back_link_params": {"href": "#"},
            }
        )
        return context

    def form_valid(self, form):
        item = self.reading_session_item
        Reading.objects.create(
            study=item.study,
            reader=self.request.user,
            opinion=Opinions.TECHNICAL_RECALL,
        )
        return super().form_valid(form)
