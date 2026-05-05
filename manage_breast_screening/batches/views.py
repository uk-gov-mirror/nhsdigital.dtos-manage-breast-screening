from logging import getLogger

from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse

from manage_breast_screening.batches.forms import BatchForm
from manage_breast_screening.batches.models import Batch
from manage_breast_screening.core.feature_flags import FeatureFlag

logger = getLogger(__name__)


def index(request):
    if FeatureFlag.is_enabled("batches"):
        batches = Batch.objects.all()
        return render(request, "index.jinja", {"batches": batches})
    else:
        raise Http404("Batches feature is not enabled")


def upload_csv(request):
    if FeatureFlag.is_enabled("batches"):
        if request.method == "POST":
            form = BatchForm(request.POST, request.FILES)
            if form.is_valid():
                try:
                    form.save()
                    messages.add_message(
                        request,
                        messages.SUCCESS,
                        "Batch uploaded successfully.",
                    )

                    return redirect(reverse("batches:index"))
                except Exception as e:
                    logger.exception(f"Batch upload failed: {e}")
                    messages.add_message(
                        request,
                        messages.INFO,
                        "Batch upload failed.",
                    )
        else:
            form = BatchForm()
        return render(request, "upload_csv.jinja", {"form": form})

    else:
        raise Http404("Batches feature is not enabled")
