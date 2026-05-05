from logging import getLogger

from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse

from manage_breast_screening.batches.forms import BatchForm

logger = getLogger(__name__)


def upload_csv(request):
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
