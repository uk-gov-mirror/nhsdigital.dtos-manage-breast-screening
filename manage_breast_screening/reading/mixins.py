from functools import cached_property

from django.http import Http404

from manage_breast_screening.dicom.models import ReadingSessionItem


class ReadingMixin:
    """
    A view mixin that exposes the reading session item, scoped to the current provider.
    """

    pk_url_kwarg = "pk"

    @cached_property
    def reading_session_item(self):
        provider = self.request.user.current_provider
        try:
            return (
                ReadingSessionItem.objects.select_related(
                    "case__study__appointment__screening_episode__participant"
                )
                .filter(
                    case__study__appointment__clinic_slot__clinic__setting__provider=provider
                )
                .get(pk=self.kwargs[self.pk_url_kwarg])
            )
        except ReadingSessionItem.DoesNotExist:
            raise Http404
