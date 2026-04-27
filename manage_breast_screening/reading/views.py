from django.contrib.auth.decorators import permission_required
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from manage_breast_screening.auth.models import Permission


@require_http_methods(["GET"])
@permission_required(Permission.READ_IMAGES, raise_exception=True)
def show_reading_dashboard(request):
    return render(request, "show_readings.jinja")
